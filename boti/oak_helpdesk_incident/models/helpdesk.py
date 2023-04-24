from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    show_incident_fields = fields.Boolean(default=False)
