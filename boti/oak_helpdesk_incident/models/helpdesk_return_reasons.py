from odoo import fields, models


# Material types
class HelpdeskReturnReasons(models.Model):
    _name = "helpdesk.return.reasons"
    _description = "Helpdesk Return Reasons"
    _check_company_auto = True

    name = fields.Char(string="Reason", required="True")

    description = fields.Text()
