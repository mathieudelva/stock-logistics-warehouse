from odoo import _, api, fields, models


class MrpAvailabilityCheck(models.TransientModel):
    _name = "mrp.availability.check"
    _description = "MRP Availability Check"

    bom_id = fields.Many2one("mrp.bom", "Bill of Materials", required=True)
    product_id = fields.Many2one(
        "product.product", "Product", domain="[('type', '=', 'product')]", required=True
    )
    product_tmpl_id = fields.Many2one(
        "product.template", "Product Template", related="product_id.product_tmpl_id"
    )
    requested_qty = fields.Float(
        "Quantity", default=1.0, digits="Product Unit of Measure", required=True
    )
    product_uom_id = fields.Many2one("uom.uom", "UoM", related="product_id.uom_id")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", required=True)
    line_ids = fields.One2many("mrp.bom.line.check", "explosion_id")
    sum_line_ids = fields.One2many("mrp.bom.line.check.summarized", "explosion_id")
    type = fields.Selection(related="bom_id.type")
    name = fields.Char("Name", default="BoM Availability Check")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                domain = self.env["mrp.bom"]._bom_find_domain(
                    products=record.product_id,
                    company_id=record.warehouse_id.company_id.id,
                )
                record.bom_id = self.env["mrp.bom"].search(
                    domain, order="sequence, product_id, id", limit=1
                )

    def bom_explosion(self):
        self.ensure_one()

        def _create_bom_lines(bom, level=0, factor=self.requested_qty):
            level += 1
            for line in bom.bom_line_ids:
                line_id = self.env["mrp.bom.line.check"].create(
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
                boms = line.product_id.bom_ids
                if boms:
                    line_qty = line.product_uom_id._compute_quantity(
                        line.product_qty, boms[0].product_uom_id
                    )
                    new_factor = factor * line_qty / boms[0].product_qty
                    _create_bom_lines(boms[0], level, new_factor)

        _create_bom_lines(self.bom_id)

    def do_bom_explosion(self):
        self.bom_explosion()
        boms_lines = self.env["mrp.bom.line.check"].search([])
        domain = [("explosion_id", "=", self.id), ("product_type", "=", "product")]
        summarized_bom_lines = boms_lines.read_group(
            domain, ["product_id", "product_qty"], ["product_id"], lazy=True
        )
        for line in summarized_bom_lines:
            self.env["mrp.bom.line.check.summarized"].create(
                {
                    "product_id": line["product_id"][0],
                    "product_qty": line["product_qty"],
                    "warehouse_id": self.warehouse_id.id,
                    "explosion_id": self.id,
                }
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Availability Check"),
            "res_model": "mrp.availability.check",
            "target": "current",
            "views": [
                (
                    self.env.ref(
                        "mrp_availability_check.mrp_availability_check_view_form2"
                    ).id,
                    "form",
                )
            ],
            "res_id": self.id,
        }


class BomLineCheck(models.TransientModel):
    _name = "mrp.bom.line.check"
    _description = "MRP Availability Check Bom Line"

    explosion_id = fields.Many2one("mrp.availability.check", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    bom_level = fields.Integer("BoM Level", readonly=True)
    product_qty = fields.Float(
        "Requested Qty", readonly=True, digits="Product Unit of Measure"
    )
    product_uom_id = fields.Many2one("uom.uom", "UoM", readonly=True)
    bom_line = fields.Many2one("mrp.bom.line", "BoM line", readonly=True)
    bom_id = fields.Many2one("mrp.bom", "BoM", related="bom_line.bom_id", readonly=True)
    product_type = fields.Selection(
        string="Product_type", related="product_id.type", readonly=True
    )
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", readonly=True)


class BomLineSummarize(models.TransientModel):
    _name = "mrp.bom.line.check.summarized"
    _description = "MRP Availability Check Bom Line Summarized"

    explosion_id = fields.Many2one("mrp.availability.check", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    product_qty = fields.Float(
        "Product Qty", readonly=True, digits="Product Unit of Measure"
    )
    product_uom_id = fields.Many2one(
        "uom.uom", "UoM", related="product_id.uom_id", readonly=True
    )
    product_type = fields.Selection(
        string="Product_type", related="product_id.type", readonly=True
    )
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", readonly=True)
    qty_available = fields.Float("On Hand Qty", compute="_compute_qty_in_source_loc")
    qty_virtual = fields.Float("Forecast Qty", compute="_compute_qty_in_source_loc")
    qty_incoming = fields.Float("Incoming Qty", compute="_compute_qty_in_source_loc")
    qty_outgoing = fields.Float("Outgoing Qty", compute="_compute_qty_in_source_loc")
    free_qty = fields.Float("Free To Use Qty", compute="_compute_qty_in_source_loc")
    qty_delta = fields.Float("Available Qty", compute="_compute_net_qty", readonly=True)
    available = fields.Boolean(
        "Available", compute="_compute_net_qty", readonly=True, default=False
    )

    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action["context"] = {
            "active_id": self.product_id.id,
            "active_model": "product.product",
            "warehouse": self.warehouse_id.id,
        }
        return action

    def _compute_qty_in_source_loc(self):
        for record in self:
            if record.product_id.type == "product":
                product = record.product_id
                record.qty_available = product.with_context(
                    warehouse=record.warehouse_id.id
                ).qty_available
                record.qty_virtual = product.with_context(
                    warehouse=record.warehouse_id.id
                ).virtual_available
                record.qty_incoming = product.with_context(
                    warehouse=record.warehouse_id.id
                ).incoming_qty
                record.qty_outgoing = product.with_context(
                    warehouse=record.warehouse_id.id
                ).outgoing_qty
                record.free_qty = product.with_context(
                    warehouse=record.warehouse_id.id
                ).free_qty
            else:
                record.qty_available = False
                record.qty_virtual = False
                record.qty_incoming = False
                record.qty_outgoing = False
                record.free_qty = False
        return True

    @api.onchange("product_qty", "free_qty")
    def _compute_net_qty(self):
        for record in self:
            record.available = False
            record.qty_delta = False
            if record.product_id.type == "product":
                record.qty_delta = record.qty_virtual - record.product_qty
            if record.qty_delta >= 0.0 or record.product_id.type != "product":
                record.available = True
        return True
