import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_round


class MrpConfirmation(models.TransientModel):
    _name = "mrp.confirmation"
    _description = "MRP Confirmation"

    date_start = fields.Datetime("Start Date", required=True)
    date_end = fields.Datetime("End Date", compute="_compute_date_end")
    setup_duration = fields.Float("Setup Duration")
    teardown_duration = fields.Float("Cleanup Duration")
    working_duration = fields.Float("Working Duration", required=True)
    overall_duration = fields.Float(
        "Overall Duration", compute="_compute_overall_duration"
    )
    production_id = fields.Many2one(
        "mrp.production",
        "Production Order",
        domain=[
            ("picking_type_id.active", "=", True),
            ("workorder_ids", "not in", []),
            ("state", "in", ("confirmed", "progress")),
        ],
    )
    product_id = fields.Many2one(
        "product.product", "Product", related="production_id.product_id", readonly=True
    )
    tracking = fields.Selection(related="product_id.tracking")
    final_lot_id = fields.Many2one(
        "stock.lot", "Lot/Serial Number", domain=[("product_id", "=", product_id)]
    )
    workorder_id = fields.Many2one(
        "mrp.workorder",
        "Workorder",
        domain="[('state', 'not in', ['done', 'cancel']), ('production_id','=',production_id)]",
    )
    qty_production = fields.Float(
        "Manufacturing Order Qty", readonly=True, related="workorder_id.qty_production"
    )
    qty_output_wo = fields.Float("WO Quantity", digits="Product Unit of Measure")
    product_uom_id = fields.Many2one(
        "uom.uom",
        "Unit of Measure",
        related="production_id.product_uom_id",
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users", string="User", required=True, default=lambda self: self.env.user
    )
    company_id = fields.Many2one(
        "res.company", "Company", related="production_id.company_id", readonly=True
    )
    milestone = fields.Boolean("Milestone", related="workorder_id.milestone")
    final_confirmation = fields.Boolean("Final Confirmation")
    check_ids = fields.One2many(related="workorder_id.check_ids")

    @api.depends("setup_duration", "teardown_duration", "working_duration")
    def _compute_overall_duration(self):
        overall_duration = 0.0
        for record in self:
            overall_duration = (
                record.setup_duration
                + record.teardown_duration
                + record.working_duration
            )
            record.overall_duration = overall_duration

    @api.depends("overall_duration", "date_start")
    def _compute_date_end(self):
        conf_duration = 0.0
        for record in self:
            record.date_end = False
            if record.overall_duration:
                conf_duration = datetime.timedelta(minutes=record.overall_duration)
                record.date_end = record.date_start + conf_duration
                if record.workorder_id.workcenter_id.resource_calendar_id:
                    calendar = record.workorder_id.workcenter_id.resource_calendar_id
                    record.date_start = calendar.plan_hours(
                        0.0, record.date_start, True
                    )
                    conf_duration = record.overall_duration / 60
                    record.date_end = calendar.plan_hours(
                        conf_duration, record.date_start, True
                    )

    @api.constrains("date_start")
    def check_date_end(self):
        if self.date_end and self.date_end > datetime.datetime.now():
            raise UserError(_("End Date in the future"))

    @api.onchange("production_id")
    def onchange_production_id(self):
        workorder_domain = [("state", "not in", ["done", "cancel"])]
        if self.production_id:
            workorder_domain += [("production_id", "=", self.production_id.id)]
            workorder_ids = self.env["mrp.workorder"].search(workorder_domain)
            if workorder_ids:
                if self.workorder_id and self.workorder_id.id not in workorder_ids.ids:
                    self.workorder_id = False

    @api.constrains("qty_output_wo")
    def check_qty_output_wo(self):
        for record in self:
            if not record.qty_output_wo > 0.0:
                raise UserError(_("Quantity has to be positive"))
            if (
                record.production_id.product_id.tracking == "serial"
                and record.qty_output_wo > 1.0
            ):
                raise UserError(
                    _("Confirmed quantity has to be 1 for product with serial number")
                )

    @api.onchange("workorder_id")
    def onchange_workorder_id(self):
        for record in self:
            # determinazione della quantita' di default
            record.qty_output_wo = record.workorder_id._get_maximum_quantity()
            # determinazione della start date di default
            if record.workorder_id.prev_work_order_id.date_actual_finished_wo:
                record.date_start = (
                    record.workorder_id.prev_work_order_id.date_actual_finished_wo
                )
            else:
                record.date_start = (
                    record.workorder_id.date_planned_start_wo
                    or record.production_id.date_planned_start_pivot
                    or fields.Datetime.now()
                )
            if record.workorder_id.state == "progress":
                time_id = self.env["mrp.workcenter.productivity"].search(
                    [
                        ("workorder_id", "=", record.workorder_id.id),
                        ("date_end", "=", False),
                    ],
                    limit=1,
                )
                if time_id:
                    record.date_start = time_id.date_start

    @api.onchange("workorder_id", "qty_output_wo", "final_confirmation")
    def onchange_workorder_id_qty_output_wo(self):
        for record in self:
            if record.workorder_id:
                record.working_duration = record._get_working_duration(
                    record.workorder_id, record.qty_output_wo
                )
                record.setup_duration = (
                    record.workorder_id.workcenter_id._get_time_start(
                        record.production_id.product_id
                    )
                )
                record.teardown_duration = (
                    record.workorder_id.workcenter_id._get_time_stop(
                        record.production_id.product_id
                    )
                )
                closed_time_id = self.env["mrp.workcenter.productivity"].search(
                    [
                        ("workorder_id", "=", record.workorder_id.id),
                        ("date_end", "!=", False),
                    ],
                    limit=1,
                )
                if closed_time_id:
                    record.setup_duration = 0.0
                last_confirmation = record.get_last_confirmation()
                if not (last_confirmation or record.final_confirmation):
                    record.teardown_duration = 0.0

    def get_last_confirmation(self):
        for record in self:
            last_confirmation = False
            max_qty = record.workorder_id._get_maximum_quantity()
            prev_workorders_closed = record.production_id.workorder_ids.filtered(
                lambda x: (
                    x.sequence < record.workorder_id.sequence
                    and x.state in ("done", "cancel")
                )
            )
            prev_workorders_progress = record.production_id.workorder_ids.filtered(
                lambda x: (
                    x.sequence < record.workorder_id.sequence and x.state == "progress"
                )
            )
            if record.milestone and not prev_workorders_progress:
                if record.final_confirmation or (max_qty <= record.qty_output_wo):
                    last_confirmation = True
            elif not record.workorder_id.prev_work_order_id or prev_workorders_closed:
                # elif not record.workorder_id.prev_work_order_id:
                if record.final_confirmation or (max_qty <= record.qty_output_wo):
                    last_confirmation = True
        return last_confirmation

    def _get_working_duration(self, workorder_id, qty_output_wo):
        quantity = (
            prod_quantity
        ) = cycle_number = prod_cycle_number = duration_expected_working = 0.0
        prod_quantity = workorder_id.production_id.product_uom_qty
        prod_cycle_number = float_round(
            prod_quantity
            / workorder_id.workcenter_id._get_capacity(
                workorder_id.production_id.product_id
            ),
            precision_digits=0,
            rounding_method="UP",
        )
        duration_expected_working = (
            (
                workorder_id._get_duration_expected()
                - workorder_id.workcenter_id._get_time_start(
                    workorder_id.production_id.product_id
                )
                - workorder_id.workcenter_id._get_time_stop(
                    workorder_id.production_id.product_id
                )
            )
            * workorder_id.workcenter_id.time_efficiency
            / (100.0 * prod_cycle_number)
        )
        if duration_expected_working < 0.0:
            duration_expected_working = 0.0
        quantity = workorder_id.production_id.product_uom_id._compute_quantity(
            qty_output_wo, workorder_id.production_id.product_id.product_tmpl_id.uom_id
        )
        cycle_number = float_round(
            quantity
            / workorder_id.workcenter_id._get_capacity(
                workorder_id.production_id.product_id
            ),
            precision_digits=0,
            rounding_method="UP",
        )
        working_duration = (
            duration_expected_working
            * cycle_number
            * 100.0
            / workorder_id.workcenter_id.time_efficiency
            or 0.0
        )
        return working_duration

    # user's confirmation check
    @api.constrains("user_id", "workorder_id")
    def check_user_id(self):
        for record in self:
            if not record.workorder_id.workcenter_id.mrp_workcenter_team_id:
                raise UserError(
                    _("Please enter a Team in the Work Center %s.")
                    % record.workorder_id.workcenter_id.name
                )
            if (
                record.user_id
                not in record.workorder_id.workcenter_id.mrp_workcenter_team_id.member_ids
            ):
                raise UserError(
                    _("User responsible has not been assigned to the WC Team")
                )

    def do_confirm(self):
        qty = 0.0
        for record in self:
            # controllo qta' massima
            max_qty_output_wo = record.workorder_id._get_maximum_quantity()
            if record.qty_output_wo > max_qty_output_wo:
                raise UserError(
                    _("It is not possible to produce more than %s") % max_qty_output_wo
                )
            # controllo di chiusura senza precedenti wo in progress
            last_confirmation = record.get_last_confirmation()
            if last_confirmation:
                prev_workorders_progress = record.production_id.workorder_ids.filtered(
                    lambda x: (
                        x.sequence < record.workorder_id.sequence
                        and x.state == "progress"
                    )
                )
                if prev_workorders_progress:
                    raise UserError(_("Previous workorders still in progress"))
                # chiusura WO precedenti alla milestone
                if record.workorder_id.milestone:
                    prev_workorders = record.production_id.workorder_ids.filtered(
                        lambda x: x.sequence < record.workorder_id.sequence
                    )
                    for prev_workorder in prev_workorders:
                        if prev_workorder.state in ("ready", "pending", "waiting"):
                            qty = (
                                record.workorder_id.qty_output_wo + record.qty_output_wo
                            )
                            record.do_previous_workorders_confirmation(
                                prev_workorder, qty, record.date_start, record.date_end
                            )
                    else:
                        if any(
                            prev_workorder.state not in ("done", "cancel")
                            for prev_workorder in prev_workorders
                        ):
                            raise UserError(
                                _("previous workorders not yet closed or cancelled")
                            )
            # lotto
            record.workorder_id.finished_lot_id = record.final_lot_id
            # esecuzione
            if record.workorder_id.state in ["ready", "waiting", "pending"]:
                record.workorder_id.button_start()
            time_values = {
                "workorder_id": record.workorder_id.id,
                "workcenter_id": record.workorder_id.workcenter_id.id,
                "setup_duration": record.setup_duration,
                "teardown_duration": record.teardown_duration,
                "working_duration": record.working_duration,
                "date_start": record.date_start,
                "date_end": record.date_end,
                "user_id": record.user_id.id,
                "qty_output_confirmation": record.qty_output_wo,
                "final_confirmation": last_confirmation,
                "loss_id": self.env["mrp.workcenter.productivity.loss"]
                .search([("loss_type", "=", "productive")], limit=1)
                .id,
            }
            open_time_id = self.env["mrp.workcenter.productivity"].search(
                [
                    ("workorder_id", "=", record.workorder_id.id),
                    ("date_end", "=", False),
                ],
                limit=1,
            )
            if open_time_id:
                open_time_id.write(time_values)
            else:
                self.env["mrp.workcenter.productivity"].create(time_values)
            if last_confirmation:
                record.workorder_id.button_finish()

    def do_previous_workorders_confirmation(
        self, workorder, qty_output_wo, date_start, date_end
    ):
        workorder.button_start()
        time_values = {
            "workorder_id": workorder.id,
            "workcenter_id": workorder.workcenter_id.id,
            "setup_duration": workorder.workcenter_id._get_time_start(
                workorder.production_id.product_id
            )
            or 0.0,
            "teardown_duration": workorder.workcenter_id._get_time_stop(
                workorder.production_id.product_id
            )
            or 0.0,
            "working_duration": self._get_working_duration(workorder, qty_output_wo),
            "date_start": workorder.date_planned_start_wo,
            "date_end": workorder.date_planned_finished_wo,
            "user_id": self.user_id.id,
            "qty_output_confirmation": qty_output_wo,
            "final_confirmation": True,
            "loss_id": self.env["mrp.workcenter.productivity.loss"]
            .search([("loss_type", "=", "productive")], limit=1)
            .id,
        }
        open_time_id = self.env["mrp.workcenter.productivity"].search(
            [("workorder_id", "=", workorder.id), ("date_end", "=", False)], limit=1
        )
        if open_time_id:
            open_time_id.write(time_values)
        else:
            self.env["mrp.workcenter.productivity"].create(time_values)
        workorder.button_finish()

    def default_get(self, fields):
        default = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        if active_id:
            default["production_id"] = active_id
        return default

    def _reopen_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_generate_serial(self):
        self.ensure_one()
        self.env.ref("mrp.view_mrp_product_produce_wizard", False)
        self.final_lot_id = self.env["stock.lot"].create(
            {
                "product_id": self.product_id.id,
                "company_id": self.production_id.company_id.id,
            }
        )
        return self._reopen_form()
