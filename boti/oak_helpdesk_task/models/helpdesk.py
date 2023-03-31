from odoo import _, api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    use_tasks = fields.Boolean(
        "Use Project Tasks", help="Convert tickets into Tasks in existing projects"
    )


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    use_tasks = fields.Boolean(related="team_id.use_tasks")
    project_helpdesk_task_ids = fields.One2many(
        "project.task",
        "task_helpdesk_ticket_id",
        string="Project Tasks",
        help="Tasks generated from this ticket",
        domain=[],
    )
    project_helpdesk_task_count = fields.Integer(
        compute="_compute_project_helpdesk_task_count"
    )

    @api.depends("project_helpdesk_task_ids")
    def _compute_project_helpdesk_task_count(self):
        ticket_groups = self.env["project.task"].read_group(
            [("task_helpdesk_ticket_id", "!=", False)],
            ["id:count_distinct"],
            ["task_helpdesk_ticket_id"],
        )
        ticket_count_mapping = dict(
            map(
                lambda group: (
                    group["task_helpdesk_ticket_id"][0],
                    group["task_helpdesk_ticket_id_count"],
                ),
                ticket_groups,
            )
        )
        for ticket in self:
            ticket.project_helpdesk_task_count = ticket_count_mapping.get(ticket.id, 0)

    def action_view_project_task(self):
        project_tasks_form_view = self.env.ref("project.view_task_form2")
        project_tasks_list_view = self.env.ref("project.view_task_tree2")
        action = {"type": "ir.actions.act_window", "res_model": "project.task"}

        if len(self.project_helpdesk_task_ids) == 1:
            action.update(
                res_id=self.project_helpdesk_task_ids[0].id,
                views=[(project_tasks_form_view.id, "form")],
            )
        else:
            action.update(
                domain=[("id", "in", self.project_helpdesk_task_ids.ids)],
                views=[
                    (project_tasks_list_view.id, "tree"),
                    (project_tasks_form_view.id, "form"),
                ],
                name=_("Tasks from Ticket"),
            )
        return action

    def action_generate_project_task(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Create a new task"),
            "res_model": "helpdesk.create.task",
            "view_mode": "form",
            "target": "new",
            "context": {
                "use_tasks": True,
                "default_task_helpdesk_ticket_id": self.id,
                "default_user_id": False,
                "default_name": self.name,
            },
        }
