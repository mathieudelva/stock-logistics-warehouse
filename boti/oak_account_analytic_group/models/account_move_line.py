from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sale_line_analytic_group_id = fields.Many2one(
        "account.analytic.plan", "Sales Type", help="Sales Type (Pool)"
    )
