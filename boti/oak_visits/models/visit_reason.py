from odoo import fields, models


# visit assessments
class VisitReason(models.Model):
    _name = "visit.reason"
    _description = "Visit Reasons"
    _check_company_auto = True

    name = fields.Char(name="Purpose", required="True", help="Reason for Partner Visit")
    description = fields.Text(name="Description")
