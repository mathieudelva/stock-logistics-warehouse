from odoo import fields, models


# Material types
class HelpdeskIncidentCause(models.Model):
    _name = "helpdesk.incident.cause"
    _description = "Helpdesk Incident Causes"
    _check_company_auto = True

    name = fields.Char(string="Cause", required="True")

    description = fields.Text()
