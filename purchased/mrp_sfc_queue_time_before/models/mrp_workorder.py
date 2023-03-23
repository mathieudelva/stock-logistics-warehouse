from datetime import timedelta

from odoo import _, api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    queue_time_before = fields.Float(
        "Queue Time Before",
        compute="_get_queue_time_before",
        store=True,
        readonly=False,
    )
    qtb_duration_expected = fields.Float(
        "Expected duration with QTB", compute="_get_qtb_duration_expected", store=True
    )
    qtb_date_planned_start_wo = fields.Datetime(
        "Scheduled Start Date",
        readonly=True,
        states={
            "waiting": [("readonly", False)],
            "ready": [("readonly", False)],
            "pending": [("readonly", False)],
        },
        compute="_compute_qtb_date_planned_start_wo",
        store=True,
    )

    def workorder_start_checks(self):
        for workorder in self:
            if not workorder.qtb_date_planned_start_wo:
                raise UserError(_("Manufacturing Order not scheduled yet"))
            if workorder.qty_output_wo > workorder.qty_production:
                raise UserError(
                    _(
                        "It is not possible to produce more than production order quantity"
                    )
                )

    @api.depends("date_planned_start_wo", "queue_time_before")
    def _compute_qtb_date_planned_start_wo(self):
        for workorder in self:
            if (
                workorder.date_planned_start_wo
                and not workorder.qtb_date_planned_start_wo
            ):
                workorder.qtb_date_planned_start_wo = (
                    workorder.date_planned_start_wo
                    + timedelta(minutes=workorder.queue_time_before)
                )
                calendar = workorder.workcenter_id.resource_calendar_id
                if calendar:
                    workorder.qtb_date_planned_start_wo = calendar.plan_hours(
                        workorder.queue_time_before / 60,
                        workorder.date_planned_start_wo,
                        True,
                    )

    @api.depends("operation_id")
    def _get_queue_time_before(self):
        queue_time_before = 0.0
        for workorder in self:
            if workorder.operation_id:
                queue_time_before = workorder.operation_id.queue_time_before
            workorder.queue_time_before = queue_time_before

    @api.depends("duration_expected", "queue_time_before")
    def _get_qtb_duration_expected(self):
        for workorder in self:
            workorder.qtb_duration_expected = (
                workorder.duration_expected + workorder.queue_time_before
            ) or 0.0

    def forwards_scheduling(self):
        for workorder in self:
            calendar = workorder.workcenter_id.resource_calendar_id
            workorder.date_planned_finished_wo = calendar.plan_hours(
                workorder.duration_expected / 60,
                workorder.qtb_date_planned_start_wo,
                compute_leaves=True,
            )

    #######################
    def backwards_scheduling_mid(self, new_date_planned):
        for workorder in self:
            expected_duration = workorder.duration_expected
            queue_time_before = workorder.queue_time_before
            qtb_duration_expected = expected_duration + queue_time_before
            workorder.write({"date_planned_finished_wo": new_date_planned})
            workorder.date_planned_start_wo = (
                workorder.date_planned_finished_wo
                - timedelta(minutes=qtb_duration_expected)
            )
            workorder.qtb_date_planned_start_wo = (
                workorder.date_planned_start_wo + timedelta(minutes=queue_time_before)
            )
            calendar = workorder.workcenter_id.resource_calendar_id
            if calendar:
                workorder.date_planned_start_wo = calendar.plan_hours(
                    -qtb_duration_expected / 60,
                    workorder.date_planned_finished_wo,
                    True,
                )
                workorder.qtb_date_planned_start_wo = calendar.plan_hours(
                    queue_time_before / 60, workorder.date_planned_start_wo, True
                )

    def forwards_scheduling_mid(self, new_date_planned):
        for workorder in self:
            expected_duration = workorder.duration_expected
            queue_time_before = workorder.queue_time_before
            qtb_duration_expected = expected_duration + queue_time_before
            workorder.date_planned_start_wo = new_date_planned
            workorder.date_planned_finished_wo = (
                workorder.date_planned_start_wo
                + timedelta(minutes=qtb_duration_expected)
            )
            workorder.qtb_date_planned_start_wo = (
                workorder.date_planned_start_wo + timedelta(minutes=queue_time_before)
            )
            calendar = workorder.workcenter_id.resource_calendar_id
            if calendar:
                workorder.date_planned_finished_wo = calendar.plan_hours(
                    qtb_duration_expected / 60, workorder.date_planned_start_wo, True
                )
                workorder.qtb_date_planned_start_wo = calendar.plan_hours(
                    queue_time_before / 60, workorder.date_planned_start_wo, True
                )

    #####################################
    @api.constrains("date_planned_start_wo", "date_planned_finished_wo")
    def _change_scheduled_dates(self):
        for workorder in self:
            date_planned_start = (
                workorder.qtb_date_planned_start_wo or workorder.date_planned_start_wo
            )
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
                        workorder.date_planned_finished
                        and date_planned_start > workorder.date_planned_finished
                    ):
                        workorder.date_planned_finished = date_planned_finish
                        workorder.date_planned_start = date_planned_start
                    else:
                        workorder.date_planned_start = date_planned_start
                        workorder.date_planned_finished = date_planned_finish


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_unplan(self):
        res = super().button_unplan()
        for workorder in self.workorder_ids:
            workorder.qtb_date_planned_start_wo = False
        return res

    def button_plan(self):
        for workorder in self.workorder_ids:
            workorder.qtb_date_planned_start_wo = False
        return super().button_plan()
