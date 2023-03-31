from odoo import fields, models


class Task(models.Model):
    _inherit = "project.task"

    task_helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Helpdesk Ticket",
        help="Ticket this Task was generated from",
        readonly=True,
        domain=[],
    )

    def action_view_task_ticket(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "form",
            "res_id": self.task_helpdesk_ticket_id.id,
        }
