# Copyright (c) OpenValue All Rights Reserved


from datetime import datetime, timedelta
from math import ceil

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

SUPPLY_METHOD_SELECTION = [
    ("buy", "Buy"),
    ("none", "Undefined"),
    ("manufacture", "Produce"),
    ("transfer", "Stock Transfer"),
    ("subcontracting", "Subcontracting"),
]


class MRPParameter(models.Model):
    _name = "mrp.parameter"
    _description = "MRP Planning Parameters"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "warehouse_id, abc_classification, mrp_type, llc DESC"

    LOT_QTY_METHOD = [
        ("E", "lot for lot"),
        ("F", "fixed order quantity"),
        ("S", "supply coverage days"),
        ("R", "replenishment maximum quantity"),
    ]

    MRP_TYPE = [
        ("M", "MRP"),
        ("R", "Reorder Point"),
    ]

    REQUIREMENTS_METHOD = [
        ("N", "no requirements"),
        ("C", "confirmed requirements in LT"),
        ("A", "all requirements in LT"),
    ]

    DEMAND_SELECTION = [
        ("00", "No Demand Management"),
        ("10", "Make To Stock"),
        ("20", "Make To Order"),
        ("30", "Planning production by lots"),
        ("40", "Planning with final assembly"),
        ("50", "Planning without final assembly"),
    ]

    ABC_SELECTION = [
        ("0", "A"),
        ("1", "B"),
        ("2", "C"),
        ("9", "R"),
    ]

    def _group_planner_domain(self):
        group = self.env.ref(
            "mrp_planning_engine.group_planning_user", raise_if_not_found=False
        )
        return [("groups_id", "in", group.ids)] if group else []

    name = fields.Char("Name")
    active = fields.Boolean(default=True)
    user_id = fields.Many2one(
        "res.users", string="MRP Planner", domain=_group_planner_domain, required=True
    )
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", required=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        related="warehouse_id.company_id",
        store=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain=[("type", "=", "product")],
    )
    product_uom = fields.Many2one(
        "uom.uom", readonly=True, related="product_id.product_tmpl_id.uom_id"
    )
    trigger = fields.Selection(
        [("auto", "Auto"), ("manual", "Manual")],
        string="Trigger",
        default="auto",
        required=True,
    )
    supply_method = fields.Selection(
        SUPPLY_METHOD_SELECTION,
        string="Supply Method",
        compute="_get_supply_method",
        compute_sudo=True,
        store=True,
    )
    abc_classification = fields.Selection(
        ABC_SELECTION,
        string="ABC Classification",
        compute="_get_abc_classification",
        store=True,
        required=True,
        readonly=False,
    )

    mrp_minimum_stock = fields.Float(
        "Safety Stock", default=0.0, digits="Product Unit of Measure"
    )
    mrp_safety_time = fields.Integer("Safety Time")
    mrp_maximum_order_qty = fields.Float(
        "Maximum Order Qty", default=0.0, digits="Product Unit of Measure"
    )
    mrp_minimum_order_qty = fields.Float(
        "Minimum Order Qty", default=0.0, digits="Product Unit of Measure"
    )
    mrp_qty_multiple = fields.Float(
        "Multiple Qty", default=1.0, digits="Product Unit of Measure"
    )

    mrp_type = fields.Selection(MRP_TYPE, "MRP Type", default="M", required=True)
    requirements_method = fields.Selection(
        REQUIREMENTS_METHOD, "Requirements Method", default="N", required=True
    )
    lot_qty_method = fields.Selection(
        LOT_QTY_METHOD, "Lot Quantity Method", default="E", required=True
    )
    mrp_fixed_qty = fields.Float(
        "Fixed Qty", default=0.0, digits="Product Unit of Measure"
    )
    mrp_coverage_days = fields.Integer("Days of Coverage")
    mrp_threshold_stock = fields.Float(
        "Reorder Point Threshold Qty", default=0.0, digits="Product Unit of Measure"
    )
    mrp_maximum_stock = fields.Float(
        "Reorder Point Maximum Qty", default=0.0, digits="Product Unit of Measure"
    )
    days_uom = fields.Many2one("uom.uom", "Days", compute="_get_uom_days")

    main_supplier_id = fields.Many2one(
        "res.partner",
        "Main Supplier",
        compute="_get_main_supplier",
        compute_sudo=True,
        store=True,
    )
    main_supplierinfo_id = fields.Many2one(
        "product.supplierinfo",
        "Main Supplier",
        compute="_get_main_supplier",
        compute_sudo=True,
        store=True,
    )
    bom_id = fields.Many2one("mrp.bom", "Bill of Materials", tracking=True)
    source_warehouse_id = fields.Many2one(
        "stock.warehouse", "Source Warehouse", compute="_get_source_warehouse"
    )

    mrp_transfer_lt = fields.Integer("Transfer LT", default=0.0)
    # gr_inspection_lt = fields.Integer("GR inspection LT", default=0.0)
    mrp_element_ids = fields.One2many("mrp.element", "mrp_parameter_id", readonly=True)
    demand_item_ids = fields.One2many("mrp.demand", "mrp_parameter_id", readonly=True)
    demand_items_count = fields.Integer(
        "Demand Items Count", compute="_demand_items_count"
    )
    planned_order_ids = fields.One2many(
        "mrp.planned.order", "mrp_parameter_id", readonly=True
    )
    planned_orders_count = fields.Integer(
        "Planned Orders Count", compute="_planned_orders_count"
    )
    llc = fields.Integer(string="Low Level Code", default=0, index=True)

    demand_indicator = fields.Selection(
        DEMAND_SELECTION, "Demand Management", default="00", required=True
    )
    mrp_demand_backward_day = fields.Integer(
        "Demand Backward Reduction Days", default=10
    )
    mrp_frozen_days = fields.Integer("Frozen Period", default=0)

    note = fields.Text("Planning Note")

    _sql_constraints = [
        (
            "product_mrp_area_uniq",
            "unique(product_id, warehouse_id)",
            "The product/Warehouse combination must be unique.",
        )
    ]

    @api.depends("mrp_type")
    def _get_abc_classification(self):
        for record in self:
            record.abc_classification = "2"
            if record.mrp_type == "R":
                record.abc_classification = "9"

    @api.constrains("mrp_type", "abc_classification")
    def check_abc_classification(self):
        for record in self:
            if not record.mrp_type == "R" and record.abc_classification == "9":
                raise UserError(_("Please check the ABC Classification"))

    @api.constrains("mrp_type", "demand_indicator")
    def check_rop_type(self):
        for record in self:
            if (
                record.mrp_type
                and record.mrp_type == "R"
                and record.demand_indicator != "00"
            ):
                raise UserError(
                    _(
                        "Please check the Demand Management Indicator: for ROP products no demand strategy is allowed"
                    )
                )

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        self.bom_id = False

    @api.constrains("active")
    def _check_archive(self):
        for record in self:
            if record.active == False and record.planned_order_ids:
                raise UserError(_("Planned Orders exist: please delete them before"))

    @api.constrains("warehouse_id", "product_id")
    def _check_supply_method(self):
        for record in self:
            if record.supply_method == "none":
                raise UserError(
                    _(
                        "Supply Method has not been determined, please check routes in product master data"
                    )
                )

    def unlink(self):
        for record in self:
            if record.planned_order_ids:
                raise UserError(_("Planned Orders exist, please delete them before."))
            if record.demand_item_ids:
                raise UserError(_("Demand Items exist, please delete them before."))
            polines = self.env["purchase.order.line"].search(
                [
                    ("state", "in", ("draft", "sent", "to approve")),
                    ("product_id", "=", record.product_id.id),
                    (
                        "order_id.picking_type_id.warehouse_id",
                        "=",
                        record.warehouse_id.id,
                    ),
                ]
            )
            if polines:
                raise UserError(
                    _("RfQ lines exist, please either convert or delete them.")
                )
            mrp_production_ids = self.env["mrp.production"].search(
                [
                    ("state", "in", ("draft", "confirmed", "progress", "to_close")),
                    ("product_id", "=", record.product_id.id),
                    ("picking_type_id.warehouse_id", "=", record.warehouse_id.id),
                ]
            )
            if mrp_production_ids:
                raise UserError(
                    _(
                        "MOs/Subcontracting POs exist, please either complete or delete them."
                    )
                )
        return super().unlink()

    def _planned_orders_count(self):
        order = self.env["mrp.planned.order"]
        for record in self:
            self.planned_orders_count = order.search_count(
                [("mrp_parameter_id", "=", record.id)]
            )

    def action_view_planned_order(self):
        context = {
            "search_default_mrp_parameter_id": [self.id],
            "default_mrp_parameter_id": self.id,
        }
        return {
            "domain": "[('mrp_parameter_id','in',["
            + ",".join(map(str, self.ids))
            + "])]",
            "context": context,
            "name": _("Planned Orders"),
            "views": [
                (
                    self.env.ref("mrp_planning_engine.mrp_planned_order_view_tree").id,
                    "tree",
                ),
                (
                    self.env.ref("mrp_planning_engine.mrp_planned_order_view_form").id,
                    "form",
                ),
            ],
            "res_model": "mrp.planned.order",
            "type": "ir.actions.act_window",
            "target": "current",
        }

    def _demand_items_count(self):
        demand = self.env["mrp.demand"]
        for record in self:
            self.demand_items_count = demand.search_count(
                [("mrp_parameter_id", "=", record.id)]
            )

    def action_view_demand_item(self):
        context = {
            "search_default_mrp_parameter_id": [self.id],
            "default_mrp_parameter_id": self.id,
        }
        return {
            "domain": "[('mrp_parameter_id','in',["
            + ",".join(map(str, self.ids))
            + "])]",
            "context": context,
            "name": _("Demand Items"),
            "views": [
                (self.env.ref("mrp_planning_engine.view_mrp_demand_tree").id, "tree"),
                (self.env.ref("mrp_planning_engine.view_mrp_demand_pivot").id, "pivot"),
                (self.env.ref("mrp_planning_engine.view_mrp_demand_graph").id, "graph"),
            ],
            "res_model": "mrp.demand",
            "type": "ir.actions.act_window",
            "target": "current",
        }

    def action_view_planning_engine_list(self):
        context = {
            "default_mrp_parameter_id": self.id,
        }
        return {
            "context": context,
            "name": _("MRP Planning Engine List"),
            "views": [
                (
                    self.env.ref(
                        "mrp_planning_engine.view_mrp_planning_engine_list_wizard"
                    ).id,
                    "form",
                )
            ],
            "res_model": "mrp.planning.engine.list",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    # @api.constrains('gr_inspection_lt')
    # def _check_gr_inspection_lt(self):
    #    for parameter in self:
    #        if parameter.gr_inspection_lt < 0:
    #            raise UserError(_('Check GR inspection Lead Time'))

    @api.constrains("mrp_threshold_stock", "mrp_type")
    def _check_mrp_threshold_stock(self):
        for parameter in self:
            if parameter.mrp_threshold_stock <= 0.0 and parameter.mrp_type == "R":
                raise UserError(
                    _("Reorder Point Threshold Quantity has to be positive")
                )

    @api.constrains("lot_qty_method", "mrp_type")
    def _check_mrp_type_lot_qty_method(self):
        for parameter in self:
            if parameter.mrp_type == "M" and parameter.lot_qty_method == "R":
                raise UserError(_("lot quantity method not allowed with mrp type"))
            if parameter.mrp_type == "R" and parameter.lot_qty_method == "S":
                raise UserError(_("lot quantity method not allowed with mrp type"))

    def _get_uom_days(self):
        uom = self.env.ref("uom.product_uom_day", raise_if_not_found=False)
        for record in self:
            if uom:
                record.days_uom = uom.id

    @api.constrains(
        "mrp_minimum_order_qty",
        "mrp_maximum_order_qty",
        "mrp_qty_multiple",
        "mrp_minimum_stock",
        "mrp_safety_time",
        "mrp_demand_backward_day",
    )
    def _check_mrp_parameters(self):
        if (
            self.mrp_minimum_order_qty < 0.0
            or self.mrp_maximum_order_qty < 0.0
            or self.mrp_qty_multiple < 0.0
            or self.mrp_minimum_stock < 0.0
            or self.mrp_safety_time < 0.0
            or self.mrp_demand_backward_day < 0.0
        ):
            raise UserError(_("planning parameters cannot be negative"))

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s-%s" % (record.product_id.name, record.warehouse_id.name)
            result.append((record.id, rec_name))
        return result

    @api.depends(
        "warehouse_id", "product_id", "product_id.seller_ids", "product_id.route_ids"
    )
    def _get_supply_method(self):
        for record in self:
            record.supply_method = record.product_id._compute_supply_method(
                record.warehouse_id
            )
            if record.supply_method != "manufacture":
                record.bom_id = False

    @api.depends(
        "product_id",
        "product_id.seller_ids",
        "product_id.seller_ids.sequence",
        "warehouse_id",
        "product_id.route_ids",
    )
    def _get_main_supplier(self):
        for record in self:
            record.main_supplierinfo_id = record.main_supplier_id = False
            if record.warehouse_id.reception_steps == "one_step":
                location = record.warehouse_id.lot_stock_id
            else:
                location = record.warehouse_id.wh_input_stock_loc_id
            values = {
                "warehouse_id": record.warehouse_id,
                "company_id": record.warehouse_id.company_id,
            }
            rule = self.env["procurement.group"]._get_rule(
                record.product_id, location, values
            )
            if rule and rule.action == "buy":
                suppliers = record.product_id._prepare_sellers()
                if suppliers:
                    record.main_supplierinfo_id = suppliers[0]
                    record.main_supplier_id = suppliers[0].partner_id

    @api.depends("warehouse_id", "product_id", "product_id.route_ids")
    def _get_source_warehouse(self):
        for record in self:
            record.source_warehouse_id = False
            if record.warehouse_id.reception_steps == "one_step":
                location = record.warehouse_id.lot_stock_id
            else:
                location = record.warehouse_id.wh_input_stock_loc_id
            values = {
                "warehouse_id": record.warehouse_id,
                "company_id": record.warehouse_id.company_id,
            }
            rule = self.env["procurement.group"]._get_rule(
                record.product_id, location, values
            )
            if rule and rule.action in ("pull", "push", "pull_push"):
                record.source_warehouse_id = rule.propagate_warehouse_id

    @api.constrains(
        "lot_qty_method", "mrp_fixed_qty", "mrp_coverage_days", "mrp_maximum_stock"
    )
    def _check_lot_method_parameters(self):
        if self.lot_qty_method == "F" and not self.mrp_fixed_qty > 0.0:
            raise UserError(_("fixed lot quantity has to be positive"))
        if self.lot_qty_method == "S" and not self.mrp_coverage_days > 0.0:
            raise UserError(_("supply coverage days parameter has to be positive"))
        if self.lot_qty_method == "R" and not self.mrp_maximum_stock > 0.0:
            raise UserError(_("maximum stock has to be positive"))

    def _get_start_date(self, finish_date):
        start_date = False
        for parameter in self:
            # gr_inspection_lt = parameter.gr_inspection_lt
            calendar = parameter.warehouse_id.calendar_id
            if (
                parameter.supply_method in ("buy", "subcontracting")
                and parameter.main_supplierinfo_id
                and calendar
            ):
                supplier_delay = parameter.main_supplierinfo_id.delay
                days_to_purchase = parameter.company_id.days_to_purchase
                # start_date = calendar.plan_days(-gr_inspection_lt, finish_date, True)
                # start_date = start_date - timedelta(days=supplier_delay)
                start_date = finish_date - timedelta(days=supplier_delay)
                start_date = calendar.plan_days(
                    -int(days_to_purchase + 1), start_date, True
                )
            elif parameter.supply_method == "manufacture" and calendar:
                manufacture_delay = parameter.product_id.produce_delay
                security_delay = parameter.company_id.manufacturing_lead
                # start_date = calendar.plan_days(-gr_inspection_lt, finish_date, True)
                # start_date = calendar.plan_days(-int(manufacture_delay+1), start_date, True)
                start_date = calendar.plan_days(
                    -int(manufacture_delay + 1), finish_date, True
                )
                if security_delay > 0.0:
                    start_date = calendar.plan_days(
                        -int(security_delay + 1), start_date, True
                    )
            elif parameter.supply_method == "transfer" and calendar:
                transfer_delay = parameter.mrp_transfer_lt
                start_date = calendar.plan_days(-transfer_delay - 1, finish_date, True)
            else:
                start_date = finish_date - relativedelta(hours=1)
        return start_date

    def _get_finish_date(self, start_date):
        finish_date = False
        for parameter in self:
            # gr_inspection_lt = parameter.gr_inspection_lt
            calendar = parameter.warehouse_id.calendar_id
            if (
                parameter.supply_method in ("buy", "subcontracting")
                and parameter.main_supplierinfo_id
                and calendar
            ):
                supplier_delay = parameter.main_supplierinfo_id.delay
                days_to_purchase = parameter.company_id.days_to_purchase
                finish_date = calendar.plan_days(
                    int(days_to_purchase + 1), start_date, True
                )
                finish_date = finish_date + timedelta(days=supplier_delay)
                # finish_date = calendar.plan_days(gr_inspection_lt, finish_date, True)
            elif parameter.supply_method == "manufacture" and calendar:
                manufacture_delay = parameter.product_id.produce_delay
                security_delay = parameter.company_id.manufacturing_lead
                finish_date = calendar.plan_days(
                    int(manufacture_delay + 1), start_date, True
                )
                if security_delay > 0.0:
                    finish_date = calendar.plan_days(
                        int(security_delay + 1), finish_date, True
                    )
                # finish_date = calendar.plan_days(gr_inspection_lt, finish_date, True)
            elif parameter.supply_method == "transfer" and calendar:
                transfer_delay = parameter.mrp_transfer_lt
                finish_date = calendar.plan_days(transfer_delay + 1, start_date, True)
            else:
                finish_date = start_date + relativedelta(hours=1)
        return finish_date

    def _in_stock_moves_domain(self, locations):
        self.ensure_one()
        return [
            ("product_id", "=", self.product_id.id),
            ("state", "not in", ["done", "cancel", "draft"]),
            ("product_qty", ">", 0.00),
            ("location_id", "not in", locations.ids),
            ("location_dest_id", "in", locations.ids),
        ]

    def _out_stock_moves_domain(self, locations):
        self.ensure_one()
        return [
            ("product_id", "=", self.product_id.id),
            ("state", "not in", ["done", "cancel", "draft"]),
            ("product_qty", ">", 0.00),
            ("location_id", "in", locations.ids),
            ("location_dest_id", "not in", locations.ids),
        ]

    def update_min_qty_from_main_supplier(self):
        for rec in self.filtered(
            lambda r: r.main_supplierinfo_id and r.supply_method == "buy"
        ):
            rec.mrp_minimum_order_qty = rec.main_supplierinfo_id.min_qty

    def _to_be_exploded(self):
        self.ensure_one()
        if self.supply_method in ("manufacture", "subcontracting"):
            return True
        else:
            return False

    def _get_lot_qty(self, qty_to_order):
        number_lots = 1
        # lot for lot
        lot_qty = qty_to_order
        for parameter in self:
            # maximum lot
            if parameter.lot_qty_method == "R":
                if (
                    max(parameter.mrp_threshold_stock, parameter.mrp_maximum_stock)
                    > qty_to_order
                ):
                    lot_qty = (
                        max(parameter.mrp_threshold_stock, parameter.mrp_maximum_stock)
                        - qty_to_order
                    )
            # fixed lot
            elif parameter.lot_qty_method == "F":
                # number_lots = int(qty_to_order // parameter.mrp_fixed_qty) + 1
                number_lots = ceil(qty_to_order / parameter.mrp_fixed_qty)
                lot_qty = parameter.mrp_fixed_qty
            # quantity constraint
            if (
                not parameter.mrp_maximum_order_qty
                and not parameter.mrp_minimum_order_qty
                and parameter.mrp_qty_multiple == 1.0
            ):
                return lot_qty, number_lots
            if lot_qty < parameter.mrp_minimum_order_qty:
                lot_qty = parameter.mrp_minimum_order_qty
            if parameter.mrp_qty_multiple:
                multiplier = ceil(lot_qty / parameter.mrp_qty_multiple)
                lot_qty = multiplier * parameter.mrp_qty_multiple
            if (
                parameter.mrp_maximum_order_qty
                and lot_qty > parameter.mrp_maximum_order_qty
            ):
                lot_qty = parameter.mrp_maximum_order_qty
        return lot_qty, number_lots

    def _prepare_data_from_stock_move(self, move, direction):
        if direction == "out":
            mrp_type = "d"
            product_qty = -move.product_qty
        elif direction == "in":
            mrp_type = "s"
            product_qty = move.product_qty
        mo = po = po_line = None
        origin = order_number = parent_product_id = mto_origin = None
        mrp_date = move.date_deadline or move.date
        if move.purchase_line_id:
            order_number = move.purchase_line_id.order_id.name
            origin = "po"
            po = move.purchase_line_id.order_id.id
            po_line = move.purchase_line_id.id
            note = False
            mto_origin = move.purchase_line_id.mto_origin
        elif move.production_id:
            production = move.production_id
            note = False
            # subcontracting header
            sub_locations = self.env["stock.location"].search(
                [
                    (
                        "id",
                        "child_of",
                        production.company_id.subcontracting_location_id.id,
                    ),
                    ("company_id", "=", production.company_id.id),
                ]
            )
            if production.location_dest_id.id in sub_locations.ids:
                origin_move = self.env["stock.move"].search(
                    [("reference", "=", move.group_id.name)], limit=1
                )
                order_number = origin_move.origin
                origin = "po"
                mto_origin = origin_move.purchase_line_id.mto_origin
                mrp_date = origin_move.date_deadline or origin_move.date
            # manufacturing order header
            else:
                order_number = production.name
                origin = "mo"
                mo = production.id
                mto_origin = production.mto_origin
        elif move.raw_material_production_id:
            production = move.raw_material_production_id
            # subcontracting item
            sub_locations = self.env["stock.location"].search(
                [
                    (
                        "id",
                        "child_of",
                        production.company_id.subcontracting_location_id.id,
                    ),
                    ("company_id", "=", production.company_id.id),
                ]
            )
            if production.location_src_id.id in sub_locations.ids:
                origin_move = self.env["stock.move"].search(
                    [("reference", "=", move.group_id.name)], limit=1
                )
                note = " ".join(
                    ["Demand PO Subcontracting Explosion: ", origin_move.name]
                )
                order_number = origin_move.origin
                parent_product_id = origin_move.product_id.id
                origin = "po"
                mto_origin = origin_move.purchase_line_id.mto_origin
            # manufacturing order item
            else:
                note = " ".join(["Demand MO Explosion: ", production.product_id.name])
                order_number = production.name
                parent_product_id = production.product_id.id
                origin = "mo"
                mo = production.id
                mto_origin = production.mto_origin
        elif move.sale_line_id:
            order_number = move.sale_line_id.order_id.name
            origin = "so"
            note = " ".join(["Delivery document: ", move.picking_id.name or move.name])
            if self.demand_indicator == "10":
                product_qty = 0.0
            elif self.demand_indicator == "00" and self.mrp_type != "R":
                product_qty = 0.0
            elif self.demand_indicator == "20":
                mto_origin = move.sale_line_id.order_id.name
        else:
            order_number = move.picking_id.name or move.name
            origin = "mv"
            note = move.picking_id.name or move.name
        return {
            "product_id": move.product_id.id,
            "mrp_parameter_id": self.id,
            "production_id": mo,
            "purchase_order_id": po,
            "purchase_line_id": po_line,
            "stock_move_id": move.id,
            "mrp_qty": product_qty,
            "mrp_date": mrp_date.date(),
            "mrp_type": mrp_type,
            "mrp_origin": origin,
            "mrp_order_number": order_number,
            "parent_product_id": parent_product_id,
            "note": note,
            "state": move.state,
            "mto_origin": mto_origin,
        }

    def _prepare_mrp_element_data_from_demand(self, demand_item):
        return {
            "product_id": demand_item.product_id.id,
            "mrp_parameter_id": self.id,
            "production_id": None,
            "purchase_order_id": None,
            "purchase_line_id": None,
            "stock_move_id": None,
            "doc_qty": demand_item.planned_qty,
            "mrp_qty": -demand_item.mrp_qty,
            "mrp_date": fields.Datetime.from_string(demand_item.date_planned).date(),
            "mrp_type": "d",
            "mrp_origin": "di",
            "mrp_order_number": "Demand Item",
            "parent_product_id": None,
            "note": "Demand Item",
        }

    def _prepare_mrp_element_data_from_planned_order(self, planned_order):
        mrp_date = fields.Datetime.from_string(planned_order.due_date)
        release_date = fields.Datetime.from_string(planned_order.order_release_date)
        return {
            "product_id": planned_order.product_id.id,
            "mrp_parameter_id": self.id,
            "production_id": None,
            "purchase_order_id": None,
            "purchase_line_id": None,
            "stock_move_id": None,
            "mrp_qty": planned_order.mrp_qty,
            "mrp_date": mrp_date.date(),
            "release_date": release_date.date(),
            "mrp_type": "s",
            "mrp_origin": "op",
            "mrp_order_number": planned_order.name,
            "parent_product_id": None,
            "note": False,
            "fixed": planned_order.fixed,
            "forward_mode_indicator": planned_order.forward_mode_indicator,
            "rescheduled_due_date": planned_order.rescheduled_due_date,
            "mto_origin": planned_order.mto_origin,
        }

    def _prepare_mrp_element_data_from_rfq(self, po_line):
        mrp_date = fields.Datetime.from_string(po_line.date_planned)
        return {
            "product_id": po_line.product_id.id,
            "mrp_parameter_id": self.id,
            "production_id": None,
            "purchase_order_id": po_line.order_id.id,
            "purchase_line_id": po_line.id,
            "stock_move_id": None,
            "mrp_qty": po_line.product_uom_qty,
            "mrp_date": mrp_date.date(),
            "mrp_type": "s",
            "mrp_origin": "po",
            "mrp_order_number": po_line.order_id.name,
            "parent_product_id": None,
            "note": False,
            "mto_origin": po_line.mto_origin,
        }

    def _prepare_mrp_element_data_from_mo(self, mo):
        mrp_date = fields.Datetime.from_string(mo.date_planned_finished_pivot)
        return {
            "product_id": mo.product_id.id,
            "mrp_parameter_id": self.id,
            "production_id": mo.id,
            "purchase_order_id": None,
            "purchase_line_id": None,
            "stock_move_id": None,
            "mrp_qty": mo.product_uom_qty,
            "mrp_date": mrp_date.date(),
            "mrp_type": "s",
            "mrp_origin": "mo",
            "mrp_order_number": mo.name,
            "parent_product_id": None,
            "note": False,
            "mto_origin": mo.mto_origin,
        }

    def _prepare_mrp_element_data_from_mo_line(self, move):
        return {
            "product_id": move.product_id.id,
            "mrp_parameter_id": self.id,
            "production_id": move.raw_material_production_id.id,
            "purchase_order_id": None,
            "purchase_line_id": None,
            "stock_move_id": move.id,
            "mrp_qty": -move.product_uom_qty,
            "mrp_date": fields.Datetime.from_string(move.date).date(),
            "mrp_type": "d",
            "mrp_origin": "mo",
            "mrp_order_number": move.raw_material_production_id.name,
            "parent_product_id": move.raw_material_production_id.product_id.id,
            "note": "Demand MO Explosion: %s"
            % move.raw_material_production_id.product_id.name,
            "mto_origin": move.raw_material_production_id.mto_origin,
        }

    def _prepare_mrp_element_data_from_sub_rfq(self, po_line, bomline):
        mrp_date = False
        order_date = po_line.order_id.date_order
        days_to_purchase = self.company_id.days_to_purchase
        mrp_date = order_date - timedelta(days=days_to_purchase)
        if self.warehouse_id.calendar_id and not days_to_purchase == 0:
            calendar = self.warehouse_id.calendar_id
            mrp_date = calendar.plan_days(-int(days_to_purchase + 1), order_date, True)
        parent_product = po_line.product_id
        factor = (
            parent_product.product_tmpl_id.uom_id._compute_quantity(
                po_line.product_uom_qty, bomline.bom_id.product_uom_id
            )
            / bomline.bom_id.product_qty
        )
        line_quantity = factor * bomline.product_qty
        return {
            "product_id": bomline.product_id.id,
            "mrp_parameter_id": self.id,
            "production_id": None,
            "purchase_order_id": po_line.order_id.id,
            "purchase_line_id": po_line.id,
            "stock_move_id": None,
            "mrp_qty": -line_quantity,
            "mrp_date": fields.Datetime.from_string(mrp_date).date(),
            "mrp_type": "d",
            "mrp_origin": "spo",
            "mrp_order_number": po_line.order_id.name,
            "parent_product_id": parent_product.id,
            "note": "Demand PO Subcontracting Explosion: %s" % parent_product.name,
            "mto_origin": po_line.mto_origin,
        }

    def _rop_calculation(self, location_ids):
        mrp_element_in_records = (
            mrp_element_out_ready_records
        ) = mrp_element_out_all_records = False
        lot_qty = (
            number_lots
        ) = (
            mrp_element_in_qty
        ) = stock_mrp = mrp_element_out_ready_qty = mrp_element_out_all_qty = 0.0
        for mrp_parameter in self:
            to_date = mrp_parameter._get_finish_date(datetime.now()) + timedelta(days=1)
            to_date = to_date.date()
            stock_mrp = mrp_parameter.product_id._compute_qty_available_locations(
                location_ids
            )
            domain_mrp_element_in = [
                ("mrp_parameter_id", "=", mrp_parameter.id),
                ("mrp_type", "=", "s"),
                ("mrp_date", "<=", to_date),
            ]
            mrp_element_in_records = self.env["mrp.element"].search(
                domain_mrp_element_in
            )
            if mrp_element_in_records:
                mrp_element_in_qty = sum(mrp_element_in_records.mapped("mrp_qty"))
            if mrp_parameter.requirements_method == "N":
                stock_mrp += mrp_element_in_qty
            elif mrp_parameter.requirements_method == "C":
                domain_mrp_element_out_ready = [
                    ("mrp_parameter_id", "=", mrp_parameter.id),
                    ("mrp_type", "=", "d"),
                    ("mrp_date", "<=", to_date),
                    (
                        "state",
                        "in",
                        ("assigned", "waiting", "confirmed", "partially_available"),
                    ),
                ]
                mrp_element_out_ready_records = self.env["mrp.element"].search(
                    domain_mrp_element_out_ready
                )
                if mrp_element_out_ready_records:
                    mrp_element_out_ready_qty = sum(
                        mrp_element_out_ready_records.mapped("mrp_qty")
                    )
                stock_mrp += mrp_element_in_qty + mrp_element_out_ready_qty
            elif mrp_parameter.requirements_method == "A":
                domain_mrp_element_out_all = [
                    ("mrp_parameter_id", "=", mrp_parameter.id),
                    ("mrp_type", "=", "d"),
                    ("mrp_date", "<=", to_date),
                ]
                mrp_element_out_all_records = self.env["mrp.element"].search(
                    domain_mrp_element_out_all
                )
                if mrp_element_out_all_records:
                    mrp_element_out_all_qty = sum(
                        mrp_element_out_all_records.mapped("mrp_qty")
                    )
                stock_mrp += mrp_element_in_qty + mrp_element_out_all_qty
            if (
                float_compare(
                    stock_mrp,
                    mrp_parameter.mrp_threshold_stock,
                    precision_rounding=mrp_parameter.product_id.uom_id.rounding,
                )
                < 0
            ):
                lot_qty, number_lots = mrp_parameter._get_lot_qty(
                    mrp_parameter.mrp_threshold_stock - stock_mrp
                )
        return lot_qty, number_lots
