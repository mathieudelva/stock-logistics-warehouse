import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    float_round,
)

logger = logging.getLogger(__name__)


class MRPPlanningEngineRun(models.TransientModel):
    _name = "mrp.planning.engine.run"
    _description = "MRP Planning Engine Run"

    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")

    # planning run in background mode a livello di volume
    def background_massive_planning_engine_run(self):
        t_mess_id = False
        overall_message = "Planning Results:\n"
        planning_volume = self.env["mrp.planning.volume"].search([])
        counter = 0
        for record in planning_volume:
            counter += 1
            message = self.planning_engine_run(record.warehouse_id)
            if message:
                overall_message += (
                    "Warehouse: " + record.warehouse_id.name + "---" + message + "\n"
                )
        if counter > 0:
            t_mess_id = (
                self.env["mrp.planning.message"].create({"name": overall_message}).id
            )
        else:
            t_mess_id = (
                self.env["mrp.planning.message"].create({"name": "no planning run"}).id
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("MRP Planning Run Results"),
            "res_model": "mrp.planning.message",
            "res_id": t_mess_id,
            "views": [
                (
                    self.env.ref(
                        "mrp_planning_engine.view_mrp_planning_message_form"
                    ).id,
                    "form",
                )
            ],
            "target": "new",
        }

    # planning run in online mode a livello di volume
    def online_massive_planning_engine_run(self):
        t_mess_id = False
        planning_volume = self.env["mrp.planning.volume"].search([])
        counter = 0
        overall_message = "Planning Results:\n"
        for record in planning_volume:
            counter += 1
            message = self.planning_engine_run(record.warehouse_id)
            if message:
                overall_message += (
                    "Warehouse: " + record.warehouse_id.name + "---" + message + "\n"
                )
        if counter > 0:
            t_mess_id = (
                self.env["mrp.planning.message"].create({"name": overall_message}).id
            )
        else:
            t_mess_id = (
                self.env["mrp.planning.message"]
                .create({"name": "no planning result"})
                .id
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Planning Run Results"),
            "res_model": "mrp.planning.message",
            "res_id": t_mess_id,
            "views": [
                (
                    self.env.ref(
                        "mrp_planning_engine.view_mrp_planning_message_form"
                    ).id,
                    "form",
                )
            ],
            "target": "new",
        }

    # planning run in cron a livello di volume
    def massive_planning_engine_run(self):
        planning_volume = self.env["mrp.planning.volume"].search([])
        counter = 0
        for record in planning_volume:
            counter += 1
            message = self.planning_engine_run(record.warehouse_id)
            if message and record.warehouse_id.partner_id.email:
                mail_obj = self.env["mail.mail"]
                subject = " ".join(
                    [
                        "MRP Planning Run for:",
                        record.warehouse_id.name,
                        "sequence:",
                        str(counter),
                    ]
                )
                mail_data = {
                    "subject": subject,
                    "body_html": message,
                    "email_to": record.warehouse_id.partner_id.email,
                }
                mail_id = mail_obj.create(mail_data)
                mail_id.send()

    # planning run in online mode a livello di warehouse
    def action_planning_engine_run(self):
        message = self.planning_engine_run(self.warehouse_id)
        t_mess_id = False
        if message:
            t_mess_id = self.env["mrp.planning.message"].create({"name": message}).id
        else:
            t_mess_id = (
                self.env["mrp.planning.message"]
                .create({"name": "no planning result"})
                .id
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("MRP Planning Run Results"),
            "res_model": "mrp.planning.message",
            "res_id": t_mess_id,
            "views": [
                (
                    self.env.ref(
                        "mrp_planning_engine.view_mrp_planning_message_form"
                    ).id,
                    "form",
                )
            ],
            "target": "new",
        }

    def planning_engine_run(self, warehouse_id):
        message = mrp_parameters = False
        self._mrp_cleanup(warehouse_id)
        mrp_lowest_llc = self._low_level_code_calculation(warehouse_id)
        mrp_parameters = self._mrp_initialisation(warehouse_id)
        mrp_counter, mrp_planned_order_counter = self._mrp_calculation(
            mrp_lowest_llc, warehouse_id, mrp_parameters
        )
        rop_counter, rop_planned_order_counter = self._rop_calculation(
            warehouse_id, mrp_parameters
        )
        counter = mrp_counter + rop_counter
        planned_order_counter = mrp_planned_order_counter + rop_planned_order_counter
        message = _(
            "planned products: %r ; planned orders: %r"
            % (counter, planned_order_counter)
        )
        if warehouse_id.company_id.forward_planning:
            self._forward_scheduling(warehouse_id, "M")
        return message

    def _mrp_cleanup(self, warehouse_id):
        domain_element = [
            ("warehouse_id", "=", warehouse_id.id),
            ("fixed", "=", False),
            ("mrp_origin", "!=", "st"),
        ]
        self.env["mrp.element"].search(domain_element).unlink()
        domain_order = [("warehouse_id", "=", warehouse_id.id), ("fixed", "=", False)]
        self.env["mrp.planned.order"].search(domain_order).unlink()

    def _low_level_code_calculation(self, warehouse_id):
        logger.info("Start low level code calculation")
        counter = 0
        # reorder point
        llc = -1
        self.env["mrp.parameter"].search(
            [("warehouse_id", "=", warehouse_id.id), ("mrp_type", "=", "R")]
        ).write({"llc": llc})
        parameters = self.env["mrp.parameter"].search([("llc", "=", llc)])
        if parameters:
            counter = len(parameters)
        # MRP
        llc = 0
        self.env["mrp.parameter"].search(
            [("warehouse_id", "=", warehouse_id.id), ("mrp_type", "!=", "R")]
        ).write({"llc": llc})
        parameters = self.env["mrp.parameter"].search([("llc", "=", llc)])
        if parameters:
            counter = len(parameters)
        llc_recursion_limit = warehouse_id.company_id.llc_recursion_limit
        while counter:
            llc += 1
            parameters = self.env["mrp.parameter"].search([("llc", "=", llc - 1)])
            product_ids = parameters.product_id.ids
            product_template_ids = parameters.product_id.product_tmpl_id.ids
            bom_lines = self.env["mrp.bom.line"].search(
                [
                    ("product_id", "in", product_ids),
                    ("bom_id.product_tmpl_id", "in", product_template_ids),
                ]
            )
            products = bom_lines.mapped("product_id")
            self.env["mrp.parameter"].search(
                [
                    ("product_id", "in", products.ids),
                    ("warehouse_id", "=", warehouse_id.id),
                    ("mrp_type", "!=", "R"),
                ]
            ).write({"llc": llc})
            counter = self.env["mrp.parameter"].search_count([("llc", "=", llc)])
            if llc > llc_recursion_limit:
                logger.error("Recursion limit reached during LLC calculation.")
                break
        mrp_lowest_llc = llc
        logger.info("End low level code calculation")
        return mrp_lowest_llc

    def _mrp_initialisation(self, warehouse_id):
        mrp_parameters = self.env["mrp.parameter"].search(
            [("warehouse_id", "=", warehouse_id.id), ("trigger", "=", "auto")]
        )
        location_ids = warehouse_id._get_engine_locations()
        for mrp_parameter in mrp_parameters:
            self._init_mrp_element(mrp_parameter, location_ids)
        return mrp_parameters

    def _init_mrp_element(self, mrp_parameter, location_ids):
        self._init_mrp_element_from_demand(mrp_parameter)
        self._init_mrp_element_from_stock_move(mrp_parameter, location_ids)
        self._init_mrp_element_from_rfq(mrp_parameter, location_ids)
        self._init_mrp_element_draft_mo(mrp_parameter)
        self._init_mrp_element_from_fixed_planned_order(mrp_parameter)

    def _init_mrp_element_from_demand(self, mrp_parameter):
        demand_items = self.env["mrp.demand"].search(
            [("mrp_parameter_id", "=", mrp_parameter.id), ("state", "=", "done")]
        )
        for demand_item in demand_items:
            demand_item_data = mrp_parameter._prepare_mrp_element_data_from_demand(
                demand_item
            )
            self.env["mrp.element"].create(demand_item_data)

    def _init_mrp_element_from_stock_move(self, mrp_parameter, location_ids):
        in_domain = mrp_parameter._in_stock_moves_domain(location_ids)
        in_moves = self.env["stock.move"].search(in_domain)
        if in_moves:
            for move in in_moves:
                in_move_data = mrp_parameter._prepare_data_from_stock_move(
                    move, direction="in"
                )
                self.env["mrp.element"].create(in_move_data)
        out_domain = mrp_parameter._out_stock_moves_domain(location_ids)
        out_moves = self.env["stock.move"].search(out_domain)
        if out_moves:
            for move in out_moves:
                out_move_data = mrp_parameter._prepare_data_from_stock_move(
                    move, direction="out"
                )
                self.env["mrp.element"].create(out_move_data)

    def _init_mrp_element_draft_mo(self, mrp_parameter):
        mos = self.env["mrp.production"].search(
            [
                ("picking_type_id.warehouse_id", "=", mrp_parameter.warehouse_id.id),
                ("state", "=", "draft"),
                ("product_id", "=", mrp_parameter.product_id.id),
            ]
        )
        for mo in mos:
            mo_data = mrp_parameter._prepare_mrp_element_data_from_mo(mo)
            self.env["mrp.element"].create(mo_data)
        # generazione dei fabbisogni
        draft_mos = self.env["mrp.production"].search(
            [
                ("picking_type_id.warehouse_id", "=", mrp_parameter.warehouse_id.id),
                ("state", "=", "draft"),
            ]
        )
        for mo in draft_mos:
            for move in mo.move_raw_ids:
                if move.product_id == mrp_parameter.product_id:
                    mo_line_data = mrp_parameter._prepare_mrp_element_data_from_mo_line(
                        move
                    )
                    self.env["mrp.element"].create(mo_line_data)

    def _init_mrp_element_from_rfq(self, mrp_parameter, location_ids):
        picking_type_ids = (
            self.env["stock.picking.type"]
            .search(
                [
                    ("default_location_dest_id", "in", location_ids.ids),
                    ("code", "=", "incoming"),
                ]
            )
            .ids
        )
        pos = self.env["purchase.order"].search(
            [
                ("picking_type_id", "in", picking_type_ids),
                ("state", "in", ["draft", "sent", "to approve"]),
            ]
        )
        po_lines = self.env["purchase.order.line"].search(
            [
                ("order_id", "in", pos.ids),
                ("product_qty", ">", 0.0),
                ("product_id", "=", mrp_parameter.product_id.id),
            ]
        )
        for po_line in po_lines:
            rfq_element_data = mrp_parameter._prepare_mrp_element_data_from_rfq(po_line)
            self.env["mrp.element"].create(rfq_element_data)
            # generazione dei fabbisogni di subcontracting dei componenti per le RfQs di subcontracting
            if mrp_parameter.supply_method == "subcontracting":
                bom = self.env["mrp.bom"]._bom_subcontract_find(
                    product=mrp_parameter.product_id,
                    picking_type=None,
                    company_id=mrp_parameter.warehouse_id.company_id.id,
                    bom_type="subcontract",
                    subcontractor=mrp_parameter.main_supplier_id,
                )
                for bomline in bom.bom_line_ids:
                    bomline_mrp_parameter_id = self.env["mrp.parameter"].search(
                        [
                            ("product_id", "=", bomline.product_id.id),
                            ("warehouse_id", "=", mrp_parameter.warehouse_id.id),
                        ],
                        limit=1,
                    )
                    if bomline_mrp_parameter_id and not bomline.product_qty <= 0.00:
                        sub_rfq_element_data = bomline_mrp_parameter_id._prepare_mrp_element_data_from_sub_rfq(
                            po_line, bomline
                        )
                        self.env["mrp.element"].create(sub_rfq_element_data)

    def _init_mrp_element_from_fixed_planned_order(self, mrp_parameter):
        planned_orders = self.env["mrp.planned.order"].search(
            [
                ("mrp_parameter_id", "=", mrp_parameter.id),
                ("mrp_qty", ">", 0.0),
                ("due_date", "!=", False),
                ("relevant_planning", "=", True),
                ("fixed", "=", True),
            ]
        )
        for planned_order in planned_orders:
            planned_order.relevant_planning = False
            mrp_element_data = (
                mrp_parameter._prepare_mrp_element_data_from_planned_order(
                    planned_order
                )
            )
            self.env["mrp.element"].create(mrp_element_data)

    def _mrp_calculation(self, mrp_lowest_llc, warehouse_id, mrp_parameters):
        counter = planned_order_counter = llc = 0
        stock_mrp = 0.0
        release_date = mrp_date = mrp_parameters_llc = False
        location_ids = warehouse_id._get_engine_locations()
        while mrp_lowest_llc > llc:
            mrp_parameters_llc = mrp_parameters.filtered(lambda r: r.llc == llc)
            llc += 1
            for mrp_parameter in mrp_parameters_llc:
                try:
                    if not warehouse_id.calendar_id:
                        raise UserError(
                            _("Working Calendar not assigned to Warehouse %s.")
                            % warehouse_id.name
                        )
                    if (
                        mrp_parameter.supply_method == "manufacture"
                        and not mrp_parameter.bom_id
                    ):
                        raise UserError(_("no BoM has been assigned"))
                    stock_mrp = (
                        mrp_parameter.product_id._compute_qty_available_locations(
                            location_ids
                        )
                    )
                    if stock_mrp < mrp_parameter.mrp_minimum_stock or stock_mrp < 0.0:
                        qty_to_order = mrp_parameter.mrp_minimum_stock - stock_mrp
                        lot_qty, number_lots = mrp_parameter._get_lot_qty(qty_to_order)
                        if number_lots > mrp_parameter.company_id.number_maximum_lots:
                            raise UserError(_("please check lot quantity"))
                        mrp_date = mrp_parameter._get_finish_date(datetime.now())
                        # planned order creation
                        if (
                            float_round(
                                lot_qty,
                                precision_rounding=mrp_parameter.product_id.product_tmpl_id.uom_id.rounding,
                            )
                            > 0
                        ):
                            for i in range(number_lots):
                                planned_order = self.create_backward_planned_order(
                                    mrp_parameter, mrp_date, lot_qty
                                )
                                planned_order_counter += 1
                            stock_mrp += lot_qty * number_lots
                    for mrp_element_id in mrp_parameter.mrp_element_ids:
                        qty_to_order = (
                            mrp_parameter.mrp_minimum_stock
                            - stock_mrp
                            - mrp_element_id.mrp_qty
                        )
                        if qty_to_order > 0.0:
                            mrp_date = datetime.strptime(
                                str(mrp_element_id.mrp_date), DEFAULT_SERVER_DATE_FORMAT
                            )  # from date to datetime
                            if mrp_parameter.lot_qty_method == "S":
                                last_date = warehouse_id.calendar_id.plan_days(
                                    int(mrp_parameter.mrp_coverage_days), mrp_date, True
                                )  # datetime
                                domain_damand = [
                                    (
                                        "mrp_date",
                                        ">=",
                                        mrp_date.strftime(
                                            DEFAULT_SERVER_DATETIME_FORMAT
                                        ),
                                    ),
                                    (
                                        "mrp_date",
                                        "<=",
                                        last_date.strftime(
                                            DEFAULT_SERVER_DATETIME_FORMAT
                                        ),
                                    ),
                                    ("mrp_type", "=", "d"),
                                ]
                                demand_records = (
                                    mrp_parameter.mrp_element_ids.filtered_domain(
                                        domain_damand
                                    )
                                )
                                demand_mrp_qty = sum(demand_records.mapped("mrp_qty"))
                                qty_to_order = (
                                    mrp_parameter.mrp_minimum_stock
                                    - stock_mrp
                                    - demand_mrp_qty
                                )
                            lot_qty, number_lots = mrp_parameter._get_lot_qty(
                                qty_to_order
                            )
                            if (
                                number_lots
                                > mrp_parameter.company_id.number_maximum_lots
                            ):
                                raise UserError(_("please check lot quantity"))
                            if (
                                mrp_parameter.mrp_safety_time > 0
                                and warehouse_id.calendar_id
                            ):
                                mrp_date = warehouse_id.calendar_id.plan_days(
                                    -mrp_parameter.mrp_safety_time, mrp_date, True
                                )
                            # planned order creation
                            if (
                                float_round(
                                    lot_qty,
                                    precision_rounding=mrp_parameter.product_id.product_tmpl_id.uom_id.rounding,
                                )
                                > 0
                            ):
                                for i in range(number_lots):
                                    planned_order = self.create_backward_planned_order(
                                        mrp_parameter, mrp_date, lot_qty
                                    )
                                    planned_order_counter += 1
                                    # strategy 50
                                    if (
                                        mrp_parameter.demand_indicator == "50"
                                        and mrp_element_id.mrp_origin == "di"
                                    ):
                                        planned_order.conversion_indicator = False
                                    # strategy 20
                                    if mrp_parameter.demand_indicator == "20":
                                        planned_order.mto_origin = (
                                            mrp_element_id.mto_origin
                                        )
                                        planned_order.mrp_element_down_ids.mto_origin = (
                                            mrp_element_id.mto_origin
                                        )
                                stock_mrp += (
                                    mrp_element_id.mrp_qty + lot_qty * number_lots
                                )
                        else:
                            stock_mrp += mrp_element_id.mrp_qty
                    counter += 1
                except UserError as error:
                    if error:
                        model_id = (
                            self.env["ir.model"]
                            .search([("model", "=", "mrp.parameter")])
                            .id
                        )
                        activity = self.env["mail.activity"].search(
                            [
                                ("res_id", "=", mrp_parameter.id),
                                ("res_model_id", "=", model_id),
                                ("note", "=", error.args[0]),
                            ]
                        )
                        if not activity:
                            mrp_parameter.activity_schedule(
                                "mail.mail_activity_data_warning",
                                note=error.args[0],
                                user_id=mrp_parameter.user_id.id,
                            )
        return counter, planned_order_counter

    def create_backward_planned_order(self, mrp_parameter_id, mrp_date, lot_qty):
        order_data = self._prepare_backward_planned_order_data(
            mrp_parameter_id, lot_qty, mrp_date
        )
        planned_order = self.env["mrp.planned.order"].create(order_data)
        return planned_order

    def _prepare_backward_planned_order_data(self, mrp_parameter_id, lot_qty, mrp_date):
        order_release_date = mrp_parameter_id._get_start_date(mrp_date)
        return {
            "mrp_parameter_id": mrp_parameter_id.id,
            "mrp_qty": lot_qty,
            "order_release_date": order_release_date,
            "due_date": mrp_date,
            "fixed": False,
            "forward_mode_indicator": False,
            "rescheduled_due_date": False,
        }

    def _forward_scheduling(self, warehouse_id, mrp_type):
        planned_orders = self.env["mrp.planned.order"].search(
            [
                ("mrp_type", "=", mrp_type),
                ("warehouse_id", "=", warehouse_id.id),
                ("order_release_date", "<", datetime.now()),
                ("fixed", "!=", True),
            ]
        )
        order_release_date = False
        for planned_order in planned_orders:
            planned_order.rescheduled_due_date = planned_order.due_date
            planned_order.forward_mode_indicator = True
            order_release_date = warehouse_id.calendar_id.plan_hours(
                0.0, datetime.now(), True
            )
            planned_order.due_date = planned_order.mrp_parameter_id._get_finish_date(
                order_release_date
            )
            planned_order.order_release_date = order_release_date

    def _rop_calculation(self, warehouse_id, mrp_parameters):
        counter = planned_order_counter = 0
        mrp_parameters = mrp_parameters.filtered(lambda r: r.llc == -1)
        location_ids = warehouse_id._get_engine_locations()
        for mrp_parameter in mrp_parameters:
            try:
                if not warehouse_id.calendar_id:
                    raise UserError(
                        _("Working Calendar not assigned to Warehouse %s.")
                        % warehouse_id.name
                    )
                if (
                    mrp_parameter.supply_method == "manufacture"
                    and not mrp_parameter.bom_id
                ):
                    raise UserError(_("no BoM has been assigned"))
                lot_qty, number_lots = mrp_parameter._rop_calculation(location_ids)
                if number_lots > mrp_parameter.company_id.number_maximum_lots:
                    raise UserError(_("please check lot quantity"))
                # planned order creation
                if (
                    float_round(
                        lot_qty,
                        precision_rounding=mrp_parameter.product_id.product_tmpl_id.uom_id.rounding,
                    )
                    > 0
                ):
                    for i in range(number_lots):
                        self.create_forward_planned_order(
                            mrp_parameter, datetime.now(), lot_qty
                        )
                        planned_order_counter += 1
                counter += 1
            except UserError as error:
                if error:
                    model_id = (
                        self.env["ir.model"]
                        .search([("model", "=", "mrp.parameter")])
                        .id
                    )
                    activity = self.env["mail.activity"].search(
                        [
                            ("res_id", "=", mrp_parameter.id),
                            ("res_model_id", "=", model_id),
                            ("note", "=", error.args[0]),
                        ]
                    )
                    if not activity:
                        mrp_parameter.activity_schedule(
                            "mail.mail_activity_data_warning",
                            note=error.args[0],
                            user_id=mrp_parameter.user_id.id,
                        )
        return counter, planned_order_counter

    def create_forward_planned_order(
        self, mrp_parameter_id, order_release_date, lot_qty
    ):
        order_data = self._prepare_forward_planned_order_data(
            mrp_parameter_id, lot_qty, order_release_date
        )
        planned_order = self.env["mrp.planned.order"].create(order_data)
        return planned_order

    def _prepare_forward_planned_order_data(
        self, mrp_parameter_id, lot_qty, order_release_date
    ):
        calendar = mrp_parameter_id.warehouse_id.calendar_id
        if calendar:
            order_release_date = calendar.plan_hours(0.0, order_release_date, True)
        due_date = mrp_parameter_id._get_finish_date(order_release_date)
        return {
            "mrp_parameter_id": mrp_parameter_id.id,
            "mrp_qty": lot_qty,
            "order_release_date": order_release_date,
            "due_date": due_date,
            "fixed": False,
            "forward_mode_indicator": True,
            "rescheduled_due_date": False,
        }


class MRPPlanningMessage(models.TransientModel):
    _name = "mrp.planning.message"
    _description = "MRP Planning Engine Messages"

    name = fields.Text("Result", readonly=True)
