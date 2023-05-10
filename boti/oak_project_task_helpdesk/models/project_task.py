import re

from odoo import _, api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    allow_helpesk_ticket_creation = fields.Boolean(
        "Use Helpdesk Tickets", help="Allow creation of helpdesk tickets from tasks"
    )


class ProjectTask(models.Model):
    _inherit = "project.task"

    allow_helpesk_ticket_creation = fields.Boolean(
        related="project_id.allow_helpesk_ticket_creation"
    )
    helpdesk_ticket_task_ids = fields.One2many(
        "helpdesk.ticket",
        "helpdesk_ticket_task_id",
        string="Project Tasks",
        help="Tasks generated from this ticket",
        domain=[],
    )
    helpdesk_task_count = fields.Integer(compute="_compute_helpdesk_task_count")

    @api.depends("helpdesk_ticket_task_ids")
    def _compute_helpdesk_task_count(self):
        task_groups = self.env["helpdesk.ticket"].read_group(
            [("helpdesk_ticket_task_id", "!=", False)],
            ["id:count_distinct"],
            ["helpdesk_ticket_task_id"],
        )
        task_count_mapping = dict(
            map(
                lambda group: (
                    group["helpdesk_ticket_task_id"][0],
                    group["helpdesk_ticket_task_id_count"],
                ),
                task_groups,
            )
        )
        for task in self:
            task.helpdesk_task_count = task_count_mapping.get(task.id, 0)

    def action_view_helpdesk_ticket(self):
        helpdesk_ticket_form_view = self.env.ref("helpdesk.helpdesk_ticket_view_form")
        helpdesk_ticket_list_view = self.env.ref("helpdesk.helpdesk_tickets_view_tree")
        action = {"type": "ir.actions.act_window", "res_model": "helpdesk.ticket"}

        if len(self.helpdesk_ticket_task_ids) == 1:
            action.update(
                res_id=self.helpdesk_ticket_task_ids[0].id,
                views=[(helpdesk_ticket_form_view.id, "form")],
            )
        else:
            action.update(
                domain=[("id", "in", self.helpdesk_ticket_task_ids.ids)],
                views=[
                    (helpdesk_ticket_list_view.id, "tree"),
                    (helpdesk_ticket_form_view.id, "form"),
                ],
                name=_("Tasks from Ticket"),
            )
        return action

    def action_generate_helpdesk_ticket(self):
        self.ensure_one()
        team_id = (
            self.env["helpdesk.team"].search([("name", "=", "RPO Sales")], limit=1).id
        )

        if self.description:
            description = str(self.description)
            description = description.replace("</p>", "\n")
            clean = re.compile("<.*?>")
            description = re.sub(clean, "", description)
        else:
            description = ""

        return {
            "type": "ir.actions.act_window",
            "name": _("Create a new ticket"),
            "res_model": "project.create.ticket",
            "view_mode": "form",
            "target": "new",
            "context": {
                "allow_helpesk_ticket_creation": True,
                "default_helpdesk_ticket_task_id": self.id,
                "default_user_id": False,
                "default_name": self.name,
                "default_partner_id": self.partner_id.id,
                "default_company_id": self.company_id.id,
                "default_team_id": team_id if team_id else False,
                "default_description": description,
            },
        }
