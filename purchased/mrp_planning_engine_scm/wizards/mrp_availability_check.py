from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpPlanningEngineAvailabilityCheck(models.TransientModel):
    _name = "mrp.planning.engine.availability.check"
    _description = "MRP Planning Engine Availability Check"

    product_id = fields.Many2one("product.product", "Product", required=True)
    product_tmpl_id = fields.Many2one(
        "product.template", "Product Template", related="product_id.product_tmpl_id"
    )
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", required=True)
    bom_id = fields.Many2one("mrp.bom", "Bill of Materials", required=True)
    requested_qty = fields.Float(
        "Quantity", default=1.0, digits="Product Unit of Measure", required=True
    )
    product_uom_id = fields.Many2one("uom.uom", "UoM", related="product_id.uom_id")
    mrp_parameter_id = fields.Boolean(
        "MRP PP", compute="_compute_mrp_parameter", readonly=True
    )
    line_ids = fields.One2many(
        "mrp.planning.engine.availability.check.line", "explosion_id"
    )
    bom_type = fields.Selection(related="bom_id.type")
    leadtime = fields.Float("LT (days)", related="bom_id.lt")
    dleadtime = fields.Float("DLT (days)", related="bom_id.dlt")
    cleadtime = fields.Float("CLT (days)", related="bom_id.clt")
    name = fields.Char("Name", default="MRP Planning Engine SCM Visibility")

    @api.onchange("product_id", "warehouse_id")
    def _onchange_product_id(self):
        self.ensure_one()
        if self.product_id and self.warehouse_id:
            if self.bom_id:
                domain = [
                    "|",
                    ("product_id", "=", self.product_id.id),
                    "&",
                    ("product_tmpl_id.product_variant_ids", "=", self.product_id.id),
                    ("product_id", "=", False),
                    ("type", "in", ("normal", "subcontract")),
                    "|",
                    ("picking_type_id", "=", False),
                    ("picking_type_id.warehouse_id", "=", self.warehouse_id.id),
                ]
                allowed_boms = self.env["mrp.bom"].search(domain)
                if self.bom_id not in allowed_boms:
                    self.bom_id = False

    def _compute_mrp_parameter(self):
        for record in self:
            record.mrp_parameter_id = False
            mrp_parameter = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("warehouse_id", "=", record.warehouse_id.id),
                ],
                limit=1,
            )
            if mrp_parameter:
                record.mrp_parameter_id = True

    def bom_explosion_availability_check_warehouse_id(self):
        self.ensure_one()
        self.bom_id.mrp_availability_check_warehouse_id = self.warehouse_id.id

        def _availability_check_warehouse_id_bom_lines(bom, level=0):
            level += 1
            for line in bom.bom_line_ids:
                line.mrp_availability_check_warehouse_id = self.warehouse_id.id
                boms = line.product_id.bom_ids
                if boms:
                    _availability_check_warehouse_id_bom_lines(boms[0], level)

        _availability_check_warehouse_id_bom_lines(self.bom_id)

    # def check_bom_id(self):
    #    self.ensure_one()
    #    self.bom_id = False
    #    if self.mrp_parameter_id.supply_method == 'manufacture':
    #        self.bom_id = self.mrp_parameter_id.bom_id.id
    #    elif self.mrp_parameter_id.supply_method == 'subcontracting':
    #        domain = self.env['mrp.bom']._bom_find_domain(products=self.mrp_parameter_id.product_id, company_id=self.mrp_parameter_id.warehouse_id.company_id.id)
    #        bom = self.env['mrp.bom'].search(domain, order='sequence, product_id, id', limit=1)
    #        if bom:
    #            self.bom_id = bom.id
    #    if not self.bom_id:
    #        raise UserError(_('BoM not found'))

    def bom_explosion(self):
        self.ensure_one()

        def _create_bom_lines(bom, level=0, factor=self.requested_qty):
            level += 1
            for line in bom.bom_line_ids:
                line_id = self.env[
                    "mrp.planning.engine.availability.check.line"
                ].create(
                    {
                        "product_id": line.product_id.id,
                        "bom_line": line.id,
                        "bom_level": level,
                        "product_qty": line.product_qty * factor,
                        "product_uom_id": line.product_uom_id.id,
                        "warehouse_id": self.warehouse_id.id,
                        "explosion_id": self.id,
                    }
                )
                line_id._compute_is_stock_buffered()
                boms = line.product_id.bom_ids
                if boms:
                    line_qty = line.product_uom_id._compute_quantity(
                        line.product_qty, boms[0].product_uom_id
                    )
                    new_factor = factor * line_qty / boms[0].product_qty
                    _create_bom_lines(boms[0], level, new_factor)

        _create_bom_lines(self.bom_id)

    def do_bom_explosion(self):
        # self.check_bom_id()
        self.bom_explosion_availability_check_warehouse_id()
        self.bom_explosion()
        self.env["mrp.planning.engine.availability.check.line"].search([])
        domain = [("explosion_id", "=", self.id), ("product_type", "=", "product")]
        self.compute_critical_path()
        return {
            "type": "ir.actions.act_window",
            "name": _("MRP Planning Engine Availability Check"),
            "res_model": "mrp.planning.engine.availability.check",
            "target": "current",
            "views": [
                (
                    self.env.ref(
                        "mrp_planning_engine_scm.mrp_availability_check_view_form2"
                    ).id,
                    "form",
                )
            ],
            "res_id": self.id,
        }

    def compute_critical_path(self):
        self.ensure_one()

        def _compute_critical_path(bom, level=0):
            level += 1
            lines = self.env["mrp.planning.engine.availability.check.line"].search(
                [
                    ("bom_level", "=", level),
                    ("explosion_id", "=", self.id),
                    ("is_stock", "=", False),
                    ("bom_id", "=", bom.id),
                ]
            )
            if lines.mapped("dleadtime"):
                dlt_max = max(lines.mapped("dleadtime"))
            else:
                dlt_max = 0.0
            lines_max = lines.filtered(lambda r: r.dleadtime == dlt_max)
            lines_max.write({"critical_path": True})
            for bom_line in bom.bom_line_ids:
                boms = bom_line.product_id.bom_ids
                critical_path = (
                    self.env["mrp.planning.engine.availability.check.line"]
                    .search(
                        [
                            ("bom_level", "=", level),
                            ("explosion_id", "=", self.id),
                            ("is_stock", "=", False),
                            ("product_id", "=", bom_line.product_id.id),
                            ("bom_id", "=", bom.id),
                        ],
                        limit=1,
                    )
                    .critical_path
                )
                if boms and critical_path:
                    _compute_critical_path(boms[0], level)

        _compute_critical_path(self.bom_id)


class MrpPlanningEngineAvailabilityCheckLine(models.TransientModel):
    _name = "mrp.planning.engine.availability.check.line"
    _description = "MRP Planning Engine Availability Check Line"

    explosion_id = fields.Many2one(
        "mrp.planning.engine.availability.check", readonly=True
    )
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    product_tmpl_id = fields.Many2one(
        "product.template", "Product Template", related="product_id.product_tmpl_id"
    )
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", readonly=True)
    mrp_parameter_id = fields.Boolean(
        "MRP PP", compute="_compute_mrp_parameter", readonly=True
    )
    bom_level = fields.Integer("BoM Level", readonly=True)
    product_qty = fields.Float(
        "Requested Qty", readonly=True, digits="Product Unit of Measure"
    )
    product_uom_id = fields.Many2one("uom.uom", "UoM", readonly=True)
    bom_line = fields.Many2one("mrp.bom.line", "BoM line", readonly=True)
    bom_id = fields.Many2one("mrp.bom", "BoM", related="bom_line.bom_id", readonly=True)
    product_type = fields.Selection(
        string="Product Type", related="product_id.type", readonly=True
    )
    make = fields.Boolean("Make", compute="_check_make", readonly=True)
    buy = fields.Boolean("Buy", compute="_check_buy", readonly=True)
    sub = fields.Boolean("Sub", compute="_check_buy", readonly=True)
    is_stock = fields.Boolean("Reorder Point", readonly=True)
    leadtime = fields.Float("LT (days)", related="bom_line.lt", readonly=True)
    dleadtime = fields.Float(
        "DLT (days)", related="bom_line.dlt", readonly=True, store=True
    )
    cleadtime = fields.Float("CLT (days)", related="bom_line.clt", readonly=True)
    critical_path = fields.Boolean("Critical Path")

    def _compute_is_stock_buffered(self):
        for record in self:
            record.is_stock = False
            mrp_parameter = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("warehouse_id", "=", record.warehouse_id.id),
                ],
                limit=1,
            )
            if mrp_parameter and mrp_parameter.mrp_type == "R":
                record.is_stock = True

    def _compute_mrp_parameter(self):
        for record in self:
            record.mrp_parameter_id = False
            mrp_parameter = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("warehouse_id", "=", record.warehouse_id.id),
                ],
                limit=1,
            )
            if mrp_parameter:
                record.mrp_parameter_id = True

    def _check_make(self):
        for record in self:
            product_routes = (
                record.product_id.route_ids + record.product_id.categ_id.total_route_ids
            )
            check_make = False
            warehouse_id = record.warehouse_id
            wh_make_route = warehouse_id.manufacture_pull_id.route_id
            if wh_make_route and wh_make_route <= product_routes:
                check_make = True
            else:
                make_route = False
                try:
                    make_route = self.env["stock.warehouse"]._find_global_route(
                        "mrp.route_warehouse0_manufacture", _("Manufacture")
                    )
                except UserError:
                    pass
                if make_route and make_route in product_routes:
                    check_make = True
            record.make = check_make

    def _check_buy(self):
        for record in self:
            product_routes = (
                record.product_id.route_ids + record.product_id.categ_id.total_route_ids
            )
            check_buy = False
            check_sub = False
            warehouse_id = record.warehouse_id
            wh_buy_route = warehouse_id.buy_pull_id.route_id
            if wh_buy_route and wh_buy_route <= product_routes:
                check_buy = True
            else:
                buy_route = False
                try:
                    buy_route = self.env["stock.warehouse"]._find_global_route(
                        "purchase_stock.route_warehouse0_buy", _("Buy")
                    )
                except UserError:
                    pass
                if buy_route and buy_route in product_routes:
                    check_buy = True
            suppliers = record.product_id._prepare_sellers()
            if suppliers:
                domain = self.env["mrp.bom"]._bom_find_domain(
                    products=record.product_id,
                    company_id=warehouse_id.company_id.id,
                    bom_type="subcontract",
                )
                bom = self.env["mrp.bom"].search(
                    domain, order="sequence, product_id, id", limit=1
                )
                if bom:
                    check_sub = True
                    check_buy = False
            record.buy = check_buy
            record.sub = check_sub
