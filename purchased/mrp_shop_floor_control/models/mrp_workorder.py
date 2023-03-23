from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"
    _order = "production_id, sequence, duration_expected, id"

    # Odoo Standard
    qty_production = fields.Float("Manufacturing Order Qty")
    # SFC
    date_actual_start_wo = fields.Datetime(
        "Actual Start Date", compute="_compute_dates_actual", store=True
    )
    date_actual_finished_wo = fields.Datetime(
        "Actual End Date", compute="_compute_dates_actual", store=True
    )
    date_planned_start_wo = fields.Datetime(
        "Scheduled Start Date",
        readonly=True,
        states={
            "waiting": [("readonly", False)],
            "ready": [("readonly", False)],
            "pending": [("readonly", False)],
        },
        copy=False,
    )
    date_planned_finished_wo = fields.Datetime(
        "Scheduled End Date",
        readonly=True,
        states={
            "waiting": [("readonly", False)],
            "ready": [("readonly", False)],
            "pending": [("readonly", False)],
        },
        copy=False,
    )
    qty_output_prev_wo = fields.Float(
        "Previous WO Quantity",
        digits="Product Unit of Measure",
        compute="_compute_prev_work_order",
    )
    prev_work_order_id = fields.Many2one(
        "mrp.workorder", "Previous Work Order", compute="_compute_prev_work_order"
    )
    milestone = fields.Boolean(
        "Milestone",
        compute="_get_milestone",
        store=True,
        readonly=True,
        states={
            "waiting": [("readonly", False)],
            "ready": [("readonly", False)],
            "pending": [("readonly", False)],
        },
        copy=True,
    )
    sequence = fields.Integer(
        "Sequence",
        compute="_get_sequence",
        store=True,
        readonly=True,
        states={
            "waiting": [("readonly", False)],
            "ready": [("readonly", False)],
            "pending": [("readonly", False)],
        },
        copy=True,
    )
    hours_uom = fields.Many2one("uom.uom", "Hours", related="workcenter_id.hours_uom")
    wo_capacity_requirements = fields.Float(
        "WO Capacity Requirements", compute="_wo_capacity_requirement", store=True
    )
    overall_duration = fields.Float(
        "Overall Duration", compute="_compute_overall_duration", store=True
    )
    mrp_workcenter_team_id = fields.Many2one(
        related="workcenter_id.mrp_workcenter_team_id", store=True
    )
    qty_output_wo = fields.Float(
        "WO Quantity",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty_output_wo",
    )
    final_confirmation = fields.Boolean(
        "Final Confirmation", readonly=True, compute="_get_final_confirmation"
    )

    # gestione backorders
    def _plan_workorder(self, replan=False):
        super()._plan_workorder(replan=False)
        for workorder in self:
            if not workorder.date_planned_start:
                workorder.date_planned_start = datetime.now()
            if not workorder.date_planned_finished:
                workorder.date_planned_finished = datetime.now()

    @api.depends("time_ids", "time_ids.qty_output_confirmation")
    def _compute_qty_output_wo(self):
        for workorder in self:
            time_ids = self.env["mrp.workcenter.productivity"].search(
                [("workorder_id", "=", workorder.id), ("date_end", "!=", False)]
            )
            workorder.qty_output_wo = (
                sum(time_ids.mapped("qty_output_confirmation")) or 0.0
            )

    @api.depends("time_ids.final_confirmation")
    def _get_final_confirmation(self):
        for workorder in self:
            workorder.final_confirmation = any(
                time_id.final_confirmation for time_id in workorder.time_ids
            )

    def _get_maximum_quantity(self):
        max_qty = 0.0
        for workorder in self:
            max_qty = workorder.qty_output_prev_wo - workorder.qty_output_wo
            if workorder.milestone:
                prev_workorders_not_open = (
                    workorder.production_id.workorder_ids.filtered(
                        lambda x: (
                            x.sequence < workorder.sequence
                            and x.state in ("done", "progress")
                        )
                    )
                )
                if prev_workorders_not_open:
                    max_qty = (
                        min(prev_workorders_not_open.mapped("qty_output_wo"))
                        - workorder.qty_output_wo
                    )
                else:
                    max_qty = workorder.qty_production - workorder.qty_output_wo
            if workorder.production_id.product_id.tracking == "serial":
                max_qty = min(workorder.qty_output_prev_wo, 1)
        return max_qty

    @api.depends("operation_id")
    def _get_milestone(self):
        for workorder in self:
            if workorder.operation_id and workorder.operation_id.milestone:
                workorder.milestone = True

    @api.depends("operation_id")
    def _get_sequence(self):
        for workorder in self:
            if workorder.operation_id and workorder.operation_id.sequence:
                workorder.sequence = workorder.operation_id.sequence

    @api.depends("time_ids.overall_duration")
    def _compute_overall_duration(self):
        for workorder in self:
            workorder.overall_duration = sum(
                workorder.time_ids.mapped("overall_duration")
            )

    @api.depends("duration_expected")
    def _wo_capacity_requirement(self):
        for workorder in self:
            workorder.wo_capacity_requirements = (workorder.duration_expected) / 60

    @api.depends("state", "qty_output_wo")
    def _compute_prev_work_order(self):
        for workorder in self:
            prev_workorders = self.search(
                [
                    ("production_id", "=", workorder.production_id.id),
                    ("sequence", "<", workorder.sequence),
                ]
            )
            if prev_workorders:
                prev_workorders_sorted = prev_workorders.sorted(
                    key=lambda r: r.sequence, reverse=True
                )
                workorder.prev_work_order_id = prev_workorders_sorted[0]
                workorder.qty_output_prev_wo = (
                    workorder.prev_work_order_id.qty_output_wo
                )
            else:
                workorder.prev_work_order_id = False
                workorder.qty_output_prev_wo = workorder.production_id.product_qty

    @api.constrains("milestone", "sequence")
    def ckeck_milestone(self):
        for workorder in self:
            other_workorders = self.search(
                [
                    ("production_id", "=", workorder.production_id.id),
                    ("id", "!=", workorder.id),
                ]
            )
            if workorder.milestone:
                milestone_sequence = workorder.sequence
                if any(
                    other_workorder.sequence == milestone_sequence
                    for other_workorder in other_workorders
                ):
                    raise UserError(_("no parallel operation is allowed for milestone"))
            else:
                workorder_sequence = workorder.sequence
                if any(
                    other_workorder.sequence == workorder_sequence
                    and other_workorder.milestone
                    for other_workorder in other_workorders
                ):
                    raise UserError(_("no parallel operation is allowed for milestone"))

    def button_start(self):
        for workorder in self:
            if not workorder.date_planned_start_wo:
                raise UserError(_("Manufacturing Order not scheduled yet"))
            if workorder.qty_output_wo > workorder.qty_production:
                raise UserError(
                    _(
                        "It is not possible to produce more than production order quantity"
                    )
                )
            if workorder.qty_output_wo == 0.0:
                if not workorder.prev_work_order_id:
                    workorder.qty_output_wo = workorder.qty_production
                else:
                    workorder.qty_output_wo = workorder.qty_output_prev_wo
            missing_components = set()
            message = ""
            missing_components.update(
                [
                    move.product_id
                    for move in workorder.production_id.move_raw_ids.filtered(
                        lambda x: x.state not in ("done", "cancel")
                    )
                    if float_compare(
                        move.product_uom_qty,
                        move.forecast_availability,
                        precision_rounding=move.product_id.uom_id.rounding,
                    )
                    > 0
                    or move.forecast_expected_date
                ]
            )
            if missing_components and not workorder.workcenter_id.start_without_stock:
                message += _(
                    "It is not possible to start workorder without components availability:\n"
                )
                message += "\n".join(component.name for component in missing_components)
            if message:
                raise UserError(message)
        return super().button_start()

    @api.depends("time_ids", "state")
    def _compute_dates_actual(self):
        date_start = False
        date_end = False
        for workorder in self:
            if workorder.state == "done" and workorder.time_ids:
                date_start = workorder.time_ids.sorted("date_start")[0].date_start
                date_end = workorder.time_ids.sorted("date_end")[-1].date_end
            workorder.date_actual_start_wo = workorder.date_start = date_start
            workorder.date_actual_finished_wo = workorder.date_finished = date_end

    # close workload
    def button_finish(self):
        super().button_finish()
        for workorder in self:
            workorder.qty_producing = workorder.qty_output_wo
            wo_capacity_ids = self.env["mrp.workcenter.capacity.load"].search(
                [("workorder_id", "=", workorder.id)]
            )
            wo_capacity_ids.unlink()
            workorder.duration_expected = workorder._get_duration_expected()

    def _get_capacity_load(self, start_date, end_date):
        sdate = start_date.date()
        edate = end_date.date()
        delta = edate - sdate
        list_days = []
        nro_hours = 0.0
        list_days.append(start_date)
        for i in range(delta.days):
            day = sdate + timedelta(days=i + 1)
            day = datetime.combine(day, datetime.min.time())
            list_days.append(day)
        list_days.append(end_date)
        for i in range(len(list_days) - 1):
            for workorder in self:
                nro_hours = (
                    workorder.workcenter_id.resource_calendar_id.get_work_duration_data(
                        list_days[i], list_days[i + 1]
                    )["hours"]
                )
                if nro_hours > 0:
                    id_created = self.env["mrp.workcenter.capacity.load"].create(
                        {
                            "workcenter_id": workorder.workcenter_id.id,
                            "workorder_id": workorder.id,
                            "product_id": workorder.production_id.product_id.id,
                            "product_qty": workorder.production_id.product_qty,
                            "product_uom_id": workorder.production_id.product_uom_id.id,
                            "date_planned": list_days[i],
                            "wo_capacity_requirements": nro_hours
                            * workorder.workcenter_id._get_capacity(
                                workorder.production_id.product_id
                            ),
                        }
                    )

    # create/change workload
    @api.constrains("date_planned_start_wo", "date_planned_finished_wo")
    def _change_scheduled_dates(self):
        for workorder in self:
            date_planned_start = workorder.date_planned_start_wo
            date_planned_finish = workorder.date_planned_finished_wo
            if date_planned_start and date_planned_finish:
                wo_capacity_ids = self.env["mrp.workcenter.capacity.load"].search(
                    [("workorder_id", "=", workorder.id)]
                )
                wo_capacity_ids.unlink()
                workorder._get_capacity_load(date_planned_start, date_planned_finish)
                if (
                    date_planned_finish
                    and date_planned_start
                    and date_planned_finish > date_planned_start
                ):
                    if (
                        date_planned_start
                        and workorder.date_planned_finished
                        and date_planned_start > workorder.date_planned_finished
                    ):
                        workorder.date_planned_finished = date_planned_finish
                        workorder.date_planned_start = date_planned_start
                    else:
                        workorder.date_planned_start = date_planned_start
                        workorder.date_planned_finished = date_planned_finish

    def backwards_scheduling(self):
        for workorder in self:
            time_delta = workorder.duration_expected
            if workorder.date_planned_finished_wo:
                workorder.date_planned_start_wo = (
                    workorder.date_planned_finished_wo - timedelta(minutes=time_delta)
                )
                calendar = workorder.workcenter_id.resource_calendar_id
                if calendar:
                    duration_expected = -workorder._get_duration_expected() / 60
                    workorder.date_planned_start_wo = calendar.plan_hours(
                        duration_expected,
                        workorder.date_planned_finished_wo,
                        compute_leaves=True,
                    )

    def forwards_scheduling(self):
        for workorder in self:
            time_delta = workorder.duration_expected
            if workorder.date_planned_start_wo:
                workorder.date_planned_finished_wo = (
                    workorder.date_planned_start_wo + timedelta(minutes=time_delta)
                )
                calendar = workorder.workcenter_id.resource_calendar_id
                if calendar:
                    duration_expected = workorder._get_duration_expected() / 60
                    workorder.date_planned_finished_wo = calendar.plan_hours(
                        duration_expected,
                        workorder.date_planned_start_wo,
                        compute_leaves=True,
                    )
