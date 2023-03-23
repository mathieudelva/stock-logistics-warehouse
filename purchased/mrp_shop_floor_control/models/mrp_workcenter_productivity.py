from odoo import api, fields, models


class MrpWorkCenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    # SFC
    setup_duration = fields.Float("Setup Duration")
    teardown_duration = fields.Float("Teardown Duration")
    working_duration = fields.Float("Working Duration")
    overall_duration = fields.Float(
        "Overall Duration", compute="_compute_overall_duration", store=True
    )
    qty_output_confirmation = fields.Float(
        "Confirmation Quantity", digits="Product Unit of Measure", copy=False
    )
    final_confirmation = fields.Boolean("Final Confirmation", copy=False)

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
