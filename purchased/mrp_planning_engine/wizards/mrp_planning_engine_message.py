from datetime import date, datetime

from odoo import _, fields, models

from odoo.addons.mrp_planning_engine.models.mrp_element import MRP_ORIGIN_SELECTION


class MRPPlanningEngineMessage(models.TransientModel):
    _name = "mrp.planning.engine.message"
    _description = "MRP Planning Engine Message"

    name = fields.Char(default="MRP Planning Engine Message List")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse", required=True)
    item_ids = fields.One2many("mrp.planning.engine.message.item", "wizard_id")
    forward_planning = fields.Boolean(
        related="warehouse_id.company_id.forward_planning", store=True
    )

    def action_planning_engine_message(self):
        today = date.today()
        today_datetime = datetime(today.year, today.month, today.day)
        # late Planned Orders
        planned_orders = self.env["mrp.planned.order"].search(
            [
                ("warehouse_id", "=", self.warehouse_id.id),
                ("order_release_date", "<", today_datetime),
            ]
        )
        for planned_order in planned_orders:
            self.env["mrp.planning.engine.message.item"].create(
                {
                    "wizard_id": self.id,
                    "mrp_parameter_id": planned_order.mrp_parameter_id.id,
                    "product_id": planned_order.product_id.id,
                    "user_id": planned_order.user_id.id,
                    "mrp_qty": planned_order.mrp_qty,
                    "product_uom": planned_order.product_uom.id,
                    "mrp_date": planned_order.due_date,
                    "rescheduled_mrp_date": False,
                    "release_date": planned_order.order_release_date,
                    "mrp_origin": "op",
                    "document_name": planned_order.name,
                    "fixed": planned_order.fixed,
                    "note": "Release date in the past",
                }
            )
        # Planned Orders in forward mode
        planned_orders = self.env["mrp.planned.order"].search(
            [
                ("mrp_type", "!=", "R"),
                ("warehouse_id", "=", self.warehouse_id.id),
                ("forward_mode_indicator", "=", True),
            ]
        )
        for planned_order in planned_orders:
            self.env["mrp.planning.engine.message.item"].create(
                {
                    "wizard_id": self.id,
                    "mrp_parameter_id": planned_order.mrp_parameter_id.id,
                    "product_id": planned_order.product_id.id,
                    "user_id": planned_order.user_id.id,
                    "mrp_qty": planned_order.mrp_qty,
                    "product_uom": planned_order.product_uom.id,
                    "mrp_date": planned_order.due_date,
                    "rescheduled_mrp_date": planned_order.rescheduled_due_date,
                    "release_date": planned_order.order_release_date,
                    "mrp_origin": "op",
                    "document_name": planned_order.name,
                    "fixed": planned_order.fixed,
                    "note": "Rescheduling in Forward Mode",
                }
            )
        # late RfQs
        location_ids = self.warehouse_id._get_engine_locations()
        incoming_picking_type_ids = self.env["stock.picking.type"].search(
            [
                ("default_location_dest_id", "in", location_ids.ids),
                ("code", "=", "incoming"),
            ]
        )
        pos = self.env["purchase.order"].search(
            [
                ("picking_type_id", "in", incoming_picking_type_ids.ids),
                ("state", "in", ["draft", "sent", "to approve"]),
                ("date_order", "<", today_datetime),
            ]
        )
        po_lines = self.env["purchase.order.line"].search(
            [("order_id", "in", pos.ids), ("product_qty", ">", 0.0)]
        )
        for po_line in po_lines:
            mrp_parameter_id = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", po_line.product_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ]
            )
            if mrp_parameter_id:
                self.env["mrp.planning.engine.message.item"].create(
                    {
                        "wizard_id": self.id,
                        "mrp_parameter_id": mrp_parameter_id.id,
                        "product_id": po_line.product_id.id,
                        "user_id": po_line.order_id.user_id.id,
                        "mrp_qty": po_line.product_qty,
                        "product_uom": po_line.product_uom.id,
                        "mrp_date": po_line.date_planned,
                        "rescheduled_mrp_date": False,
                        "release_date": po_line.order_id.date_order,
                        "mrp_origin": "po",
                        "document_name": po_line.order_id.name,
                        "fixed": False,
                        "note": "RfQ document date in the past",
                    }
                )
        # late MOs
        late_productions = self.env["mrp.production"].search(
            [
                ("picking_type_id.warehouse_id", "=", self.warehouse_id.id),
                ("state", "in", ("draft", "confirmed")),
                ("date_planned_start_pivot", "<", today_datetime),
            ]
        )
        for production in late_productions:
            mrp_parameter_id = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", production.product_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ]
            )
            if mrp_parameter_id:
                self.env["mrp.planning.engine.message.item"].create(
                    {
                        "wizard_id": self.id,
                        "mrp_parameter_id": mrp_parameter_id.id,
                        "product_id": production.product_id.id,
                        "user_id": production.user_id.id,
                        "mrp_qty": production.product_qty,
                        "product_uom": production.product_uom_id.id,
                        "mrp_date": production.date_planned_finished_pivot,
                        "rescheduled_mrp_date": False,
                        "release_date": production.date_planned_start_pivot,
                        "mrp_origin": "mo",
                        "document_name": production.name,
                        "fixed": False,
                        "note": "MO planned pivot start date in the past",
                    }
                )
        # expired POs
        in_domain = [
            ("state", "not in", ["done", "cancel"]),
            ("product_qty", ">", 0.00),
            ("location_id", "not in", location_ids.ids),
            ("location_dest_id", "in", location_ids.ids),
            ("date_deadline", "<", today_datetime),
        ]
        in_moves = self.env["stock.move"].search(in_domain)
        for move in in_moves:
            mrp_parameter_id = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ]
            )
            if mrp_parameter_id and move.purchase_line_id:
                self.env["mrp.planning.engine.message.item"].create(
                    {
                        "wizard_id": self.id,
                        "mrp_parameter_id": mrp_parameter_id.id,
                        "product_id": move.product_id.id,
                        "user_id": move.purchase_line_id.order_id.user_id.id,
                        "mrp_qty": move.product_uom_qty,
                        "product_uom": move.product_uom.id,
                        "mrp_date": move.date_deadline,
                        "rescheduled_mrp_date": False,
                        "release_date": move.purchase_line_id.order_id.date_order,
                        "mrp_origin": "po",
                        "document_name": move.purchase_line_id.order_id.name,
                        "fixed": False,
                        "note": "PO expired: delivery date in the past",
                    }
                )
        # expired MOs
        sub_locations = self.env["stock.location"].search(
            [
                (
                    "id",
                    "child_of",
                    self.warehouse_id.company_id.subcontracting_location_id.id,
                ),
                ("company_id", "=", self.warehouse_id.company_id.id),
            ]
        )
        expired_productions = self.env["mrp.production"].search(
            [
                ("picking_type_id.warehouse_id", "=", self.warehouse_id.id),
                ("state", "not in", ("done", "cancel")),
                ("location_dest_id", "not in", sub_locations.ids),
                ("date_planned_finished_pivot", "<", today_datetime),
            ]
        )
        for production in expired_productions:
            mrp_parameter_id = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", production.product_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ]
            )
            if mrp_parameter_id:
                self.env["mrp.planning.engine.message.item"].create(
                    {
                        "wizard_id": self.id,
                        "mrp_parameter_id": mrp_parameter_id.id,
                        "product_id": production.product_id.id,
                        "user_id": production.user_id.id,
                        "mrp_qty": production.product_qty,
                        "product_uom": production.product_uom_id.id,
                        "mrp_date": production.date_planned_finished_pivot,
                        "rescheduled_mrp_date": False,
                        "release_date": production.date_planned_start_pivot,
                        "mrp_origin": "mo",
                        "document_name": production.name,
                        "fixed": False,
                        "note": "MO planned pivot finish date in the past",
                    }
                )
        # expired Subcontracting POs
        expired_subcontacting_productions = self.env["mrp.production"].search(
            [
                ("picking_type_id.warehouse_id", "=", self.warehouse_id.id),
                ("state", "not in", ("done", "cancel")),
                ("location_dest_id", "in", sub_locations.ids),
                ("date_planned_finished_pivot", "<", today_datetime),
            ]
        )
        for production in expired_subcontacting_productions:
            receipt_move = self.env["stock.move"].search(
                [("reference", "=", production.procurement_group_id.name)], limit=1
            )
            po_name = receipt_move.origin
            mrp_parameter_id = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", production.product_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ]
            )
            if mrp_parameter_id:
                self.env["mrp.planning.engine.message.item"].create(
                    {
                        "wizard_id": self.id,
                        "mrp_parameter_id": mrp_parameter_id.id,
                        "product_id": production.product_id.id,
                        "user_id": production.user_id.id,
                        "mrp_qty": production.product_qty,
                        "product_uom": production.product_uom_id.id,
                        "mrp_date": production.date_planned_finished_pivot,
                        "rescheduled_mrp_date": False,
                        "release_date": production.date_planned_start_pivot,
                        "mrp_origin": "po",
                        "document_name": po_name,
                        "fixed": False,
                        "note": "PO expired: delivery date in the past",
                    }
                )
        # scheduled MOs
        scheduled_productions = self.env["mrp.production"].search(
            [
                ("picking_type_id.warehouse_id", "=", self.warehouse_id.id),
                ("state", "not in", ("done", "cancel")),
            ]
        )
        for production in scheduled_productions:
            mrp_parameter_id = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", production.product_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ]
            )
            if mrp_parameter_id:
                if (
                    production.date_planned_finished_wo
                    and production.date_planned_finished_pivot
                    < production.date_planned_finished_wo
                ):
                    self.env["mrp.planning.engine.message.item"].create(
                        {
                            "wizard_id": self.id,
                            "mrp_parameter_id": mrp_parameter_id.id,
                            "product_id": production.product_id.id,
                            "user_id": production.user_id.id,
                            "mrp_qty": production.product_qty,
                            "product_uom": production.product_uom_id.id,
                            "mrp_date": production.date_planned_finished_pivot,
                            "rescheduled_mrp_date": False,
                            "release_date": production.date_planned_start_pivot,
                            "mrp_origin": "mo",
                            "document_name": production.name,
                            "fixed": False,
                            "note": "MO scheduled finish date overcomes MO planned pivot finish date",
                        }
                    )
                # MOs to be rescheduled
                demand_mrp_element = self.env["mrp.element"].search(
                    [
                        ("mrp_parameter_id", "=", mrp_parameter_id.id),
                        ("mrp_type", "=", "d"),
                        ("mrp_date", "=", production.date_planned_finished_pivot),
                    ]
                )
                if not demand_mrp_element:
                    self.env["mrp.planning.engine.message.item"].create(
                        {
                            "wizard_id": self.id,
                            "mrp_parameter_id": mrp_parameter_id.id,
                            "product_id": production.product_id.id,
                            "user_id": production.user_id.id,
                            "mrp_qty": production.product_qty,
                            "product_uom": production.product_uom_id.id,
                            "mrp_date": production.date_planned_finished_pivot,
                            "rescheduled_mrp_date": False,
                            "release_date": production.date_planned_start_pivot,
                            "mrp_origin": "mo",
                            "document_name": production.name,
                            "fixed": False,
                            "note": "MO has to be rescheduled",
                        }
                    )
        # POs to be rescheduled
        in_domain = [
            ("state", "not in", ["done", "cancel"]),
            ("product_qty", ">", 0.00),
            ("location_id", "not in", location_ids.ids),
            ("location_dest_id", "in", location_ids.ids),
        ]
        in_moves = self.env["stock.move"].search(in_domain)
        for move in in_moves:
            mrp_parameter_id = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ]
            )
            if mrp_parameter_id and move.purchase_line_id:
                demand_mrp_element = self.env["mrp.element"].search(
                    [
                        ("mrp_parameter_id", "=", mrp_parameter_id.id),
                        ("mrp_type", "=", "d"),
                        ("mrp_date", "=", move.date_deadline),
                    ]
                )
                if not demand_mrp_element:
                    self.env["mrp.planning.engine.message.item"].create(
                        {
                            "wizard_id": self.id,
                            "mrp_parameter_id": mrp_parameter_id.id,
                            "product_id": move.product_id.id,
                            "user_id": move.purchase_line_id.order_id.user_id.id,
                            "mrp_qty": move.product_uom_qty,
                            "product_uom": move.product_uom.id,
                            "mrp_date": move.date_deadline,
                            "rescheduled_mrp_date": False,
                            "release_date": move.purchase_line_id.order_id.date_order,
                            "mrp_origin": "po",
                            "document_name": move.purchase_line_id.order_id.name,
                            "fixed": False,
                            "note": "PO has to be rescheduled",
                        }
                    )
        return {
            "type": "ir.actions.act_window",
            "name": _("MRP Planning Engine Message"),
            "res_model": "mrp.planning.engine.message",
            #'target': 'new',
            "views": [
                (
                    self.env.ref(
                        "mrp_planning_engine.view_mrp_planning_engine_message_form"
                    ).id,
                    "form",
                )
            ],
            "res_id": self.id,
        }


class MRPPlanningEngineMessageItem(models.TransientModel):
    _name = "mrp.planning.engine.message.item"
    _description = "MRP Planning Engine Message Item"
    _order = "release_date, id"

    wizard_id = fields.Many2one("mrp.planning.engine.message", readonly=True)
    mrp_parameter_id = fields.Many2one(
        "mrp.parameter", "Planning Parameter", readonly=True
    )
    product_id = fields.Many2one("product.product", readonly=True)
    user_id = fields.Many2one("res.users", string="Responsible", readonly=True)
    mrp_qty = fields.Float("MRP Quantity", readonly=True)
    product_uom = fields.Many2one("uom.uom", readonly=True)
    release_date = fields.Datetime("Release Date", readonly=True)
    mrp_date = fields.Datetime("MRP Date", readonly=True)
    rescheduled_mrp_date = fields.Datetime("Rescheduled MRP Date", readonly=True)
    supply_method = fields.Selection(
        related="mrp_parameter_id.supply_method", readonly=True
    )
    mrp_origin = fields.Selection(
        MRP_ORIGIN_SELECTION, string="Document Type", readonly=True
    )
    document_name = fields.Char("Document Name", readonly=True)
    fixed = fields.Boolean("Fixed", readonly=True)
    note = fields.Char("Exception Message", readonly=True)
