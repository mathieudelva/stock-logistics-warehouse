from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Ticket",
        help="Ticket this Project was generated from",
        readonly=True,
    )

    def action_view_ticket(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "form",
            "res_id": self.helpdesk_ticket_id.id,
        }
