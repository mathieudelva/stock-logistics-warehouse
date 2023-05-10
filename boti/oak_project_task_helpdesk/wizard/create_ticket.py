from odoo import _, fields, models


class CreateTicket(models.TransientModel):
    _name = "project.create.ticket"
    _description = "Create a Helpdesk Ticket in an existing Project Task"

    helpdesk_ticket_task_id = fields.Many2one(
        "project.task", string="Related task", required=True
    )
    company_id = fields.Many2one(related="helpdesk_ticket_task_id.company_id")
    name = fields.Char("Title", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer Contact")
    team_id = fields.Many2one("helpdesk.team", string="Helpdesk Team")
    description = fields.Text()
    # project_id is always field service

    def action_generate_helpdesk_ticket(self):
        self.ensure_one()
        return self.env["helpdesk.ticket"].create(
            {
                "name": self.name,
                "team_id": self.team_id.id,
                "partner_id": self.partner_id.id,
                "description": self.description,
                "helpdesk_ticket_task_id": self.helpdesk_ticket_task_id.id,
            }
        )

    def action_generate_and_view_project_task(self):
        self.ensure_one()
        new_ticket = self.action_generate_helpdesk_ticket()
        return {
            "type": "ir.actions.act_window",
            "name": _("Tickets from Task"),
            "res_model": "helpdesk.ticket",
            "res_id": new_ticket.id,
            "view_mode": "form",
            "view_id": self.env.ref("helpdesk.helpdesk_ticket_view_form").id,
        }
