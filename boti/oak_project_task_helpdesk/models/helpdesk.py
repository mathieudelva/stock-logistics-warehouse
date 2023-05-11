from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    helpdesk_ticket_task_id = fields.Many2one(
        "project.task",
        string="Project Task",
        help="Task this Ticket was generated from",
        readonly=True,
        domain=[],
    )

    def action_view_ticket_task(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "form",
            "res_id": self.helpdesk_ticket_task_id.id,
        }
