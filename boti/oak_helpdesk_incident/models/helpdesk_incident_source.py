from odoo import fields, models


# Material types
class HelpdeskIncidentSource(models.Model):
    _name = "helpdesk.incident.source"
    _description = "Helpdesk Incident Sources"
    _check_company_auto = True

    name = fields.Char(string="Source", required="True")

    description = fields.Text()
