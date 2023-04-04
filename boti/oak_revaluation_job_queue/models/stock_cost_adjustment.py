# Copyright 2021-2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, exceptions, models


class StockCostAdjustment(models.Model):
    _inherit = "stock.cost.adjustment"

    def _get_queue_job(self):
        self.ensure_one()
        return (
            self.env["queue.job"]
            .sudo()
            .search(
                [
                    (
                        "func_string",
                        "=",
                        "stock.cost.adjustment(%s,)._action_start()" % self.id,
                    )
                ],
                limit=1,
                order="date_started DESC",
            )
        )

    def _action_start(self):
        super()._action_start()
        job = self._get_queue_job()
        if job:
            job.user_id.notify_success(
                title=_("Cost Adjustment"),
                message=_("Impact computation completed for %s.") % self.name,
            )
        return

    def action_start(self):
        self.ensure_one()
        job = self._get_queue_job()
        if job.state in ["started", "enqueued", "pending"]:
            raise exceptions.UserError(
                _(
                    "A Job is already queued for this revaluation:\n%(job_uuid)s %(job_state)s",
                    job_uuid=job.uuid,
                    job_state=job.state,
                )
            )
        self.env.user.notify_info(
            title=_("Cost Adjustment"), message=_("Impact computation started.")
        )
        self.state = "computing"
        self.with_delay()._action_start()
        return True
