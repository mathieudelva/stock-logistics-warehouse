from odoo import fields, models


# sales line type account lookup
class SaleTypeAccount(models.Model):
    _name = "sale.type.account"
    _description = "Sales Type Account"

    name = fields.Char(string="Description")
    sale_line_analytic_group_id = fields.Many2one(
        "account.analytic.group", "Sales Type", help="Sales Type (Pool)"
    )

    account_id = fields.Many2one(
        "account.account", "Account", help="Sales Line Type Account"
    )
