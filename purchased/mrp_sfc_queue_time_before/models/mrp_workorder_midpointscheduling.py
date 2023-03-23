from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    # def _compute_capacity_load(self):
    #    date_planned_start = date_planned_finish = False
    #    for workorder in self:
    #        date_planned_start = workorder.date_planned_start_wo
    #        date_planned_finish = workorder.date_planned_finished_wo
    #        if date_planned_start and date_planned_finish:
    #            wo_capacity_ids = self.env['mrp.workcenter.capacity.load'].search([('workorder_id', '=', workorder.id)])
    #            wo_capacity_ids.unlink()
    #            workorder._get_capacity_load(date_planned_start, date_planned_finish)

    def mid_point_scheduling_engine2(self, date_start):
        for workorder in self:
            sequence_wo = workorder.sequence
            workorder.forwards_scheduling_mid(date_start)
            min_date_start = workorder.date_planned_start_wo
            max_date_finished = workorder.date_planned_finished_wo

            workorders = self.env["mrp.workorder"].search(
                [
                    ("production_id", "=", workorder.production_id.id),
                ]
            )
            # parallel workorders
            parall_workorders = workorders.filtered(
                lambda r: (
                    r.sequence == sequence_wo
                    and r.id != workorder.id
                    and r.state in ("ready", "pending", "waiting")
                )
            )
            if parall_workorders:
                for parall_workorder in parall_workorders:
                    parall_workorder.forwards_scheduling_mid(date_start)
                    max_date_finished = max(
                        parall_workorder.date_planned_finished_wo, max_date_finished
                    )

            parall_progress_workorders = workorders.filtered(
                lambda r: (
                    r.sequence == sequence_wo
                    and r.id != workorder.id
                    and r.state == "progress"
                )
            )
            if parall_progress_workorders:
                for progress_workorder in parall_progress_workorders:
                    max_date_finished = max(
                        progress_workorder.date_planned_finished_wo, max_date_finished
                    )
            # previous workorders
            prev_workorders = workorders.filtered(
                lambda r: (
                    r.sequence < sequence_wo
                    and r.state in ("ready", "pending", "waiting", "progress")
                )
            ).sorted(key=lambda r: (r.sequence, r.duration_expected), reverse=True)
            if prev_workorders:
                current_workorder = workorder
                for prev_workorder in prev_workorders:
                    # workorder precedente in progress
                    if prev_workorder.state == "progress":
                        if (
                            prev_workorder.date_planned_finished_wo
                            > current_workorder.date_planned_start_wo
                        ):
                            raise UserError(
                                _(
                                    "backward scheduling is not possible for the production order %r"
                                    % workorder.production_id.name
                                )
                            )
                    else:
                        # workorder in parallelo
                        if current_workorder.sequence == prev_workorder.sequence:
                            prev_workorder.forwards_scheduling_mid(
                                current_workorder.date_planned_start_wo
                            )
                        # workorder in sequenza
                        else:
                            prev_workorder.backwards_scheduling_mid(min_date_start)
                    min_date_start = min(
                        prev_workorder.date_planned_start_wo,
                        current_workorder.date_planned_start_wo,
                    )
                    current_workorder = prev_workorder
            # subsequent workorders
            succ_workorders = workorders.filtered(
                lambda r: (
                    r.sequence > sequence_wo
                    and r.state in ("ready", "pending", "waiting")
                )
            ).sorted(key=lambda r: r.sequence)
            if succ_workorders:
                current_workorder = workorder
                for succ_workorder in succ_workorders:
                    # workorder in parallelo
                    if current_workorder.sequence == succ_workorder.sequence:
                        succ_workorder.forwards_scheduling_mid(
                            current_workorder.date_planned_start_wo
                        )
                    # workorder in sequenza
                    else:
                        succ_workorder.forwards_scheduling_mid(max_date_finished)
                    max_date_finished = max(
                        succ_workorder.date_planned_finished_wo,
                        current_workorder.date_planned_finished_wo,
                    )
                    current_workorder = succ_workorder

            workorder.production_id.date_planned_start_wo = min_date_start
            workorder.production_id.date_planned_finished_wo = max_date_finished


class set_date_wizard(models.TransientModel):
    _name = "set.date.wizard"
    _description = "Mid Point Scheduling Wizard"

    new_date_planned_start_wo = fields.Datetime(
        string=_("New Scheduled Start Date"), required=True
    )
    workorder_id = fields.Many2one("mrp.workorder", string="Workorder", readonly=True)

    @api.model
    def default_get(self, fields):
        default = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        if active_id:
            default["workorder_id"] = active_id
        return default

    def set_date(self):
        new_date_planned = False
        workorder_id = self.env.context.get("active_id", False)
        if workorder_id:
            workorder = self.env["mrp.workorder"].browse(workorder_id)
            if workorder.state == "progress":
                raise UserError(
                    _(
                        "midpoint scheduling cannot be performed for workorder in progress"
                    )
                )
            if not (
                workorder.date_planned_start_wo or workorder.qtb_date_planned_start_wo
            ):
                raise UserError(_("Manufacturing Order not scheduled yet"))
            calendar = workorder.workcenter_id.resource_calendar_id
            new_date_planned = calendar.plan_hours(
                0.0, self.new_date_planned_start_wo, True
            )
            workorder.mid_point_scheduling_engine2(new_date_planned)
