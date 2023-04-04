from odoo import _, fields, models


class CreateTask(models.TransientModel):
    _name = "helpdesk.create.task"
    _description = "Create a Task in an existing Project"

    task_helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Related ticket", required=True
    )
    company_id = fields.Many2one(related="task_helpdesk_ticket_id.company_id")
    name = fields.Char("Title", required=True)
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        help="Project to create the task inside",
        required=True,
        domain="['&', ('is_template', '=', False), \
            '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    note = fields.Html(related="task_helpdesk_ticket_id.description")

    def action_generate_project_task(self):
        self.ensure_one()
        return self.env["project.task"].create(
            {
                "name": self.name,
                "task_helpdesk_ticket_id": self.task_helpdesk_ticket_id.id,
                "project_id": self.project_id.id,
                "description": self.note,
            }
        )

    def action_generate_and_view_project_task(self):
        self.ensure_one()
        new_task = self.action_generate_project_task()
        return {
            "type": "ir.actions.act_window",
            "name": _("Task from Tickets"),
            "res_model": "project.task",
            "res_id": new_task.id,
            "view_mode": "form",
            "view_id": self.env.ref("project.view_task_form2").id,
        }
