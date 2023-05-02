from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mo_hold = fields.Boolean(string="MO on Hold", default=False, tracking=True)

    mo_hold_reason = fields.Char(string="MO on Hold Reason", tracking=True)

    analytic_plan_id = fields.Many2one(
        related="analytic_account_id.plan_id", store=True
    )

    @api.constrains("product_id", "move_raw_ids")
    def _check_production_lines(self):
        return
