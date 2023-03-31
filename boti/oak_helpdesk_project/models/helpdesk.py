from odoo import _, api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    use_project = fields.Boolean(
        "Attach Projects", help="Convert tickets into Projects"
    )


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    use_project = fields.Boolean(related="team_id.use_project")
    project_ids = fields.One2many(
        "project.project",
        "helpdesk_ticket_id",
        string="Projects",
        help="Projects generated from this ticket",
    )
    project_count = fields.Integer(compute="_compute_project_count")

    @api.depends("project_ids")
    def _compute_project_count(self):
        ticket_groups = self.env["project.project"].read_group(
            [("helpdesk_ticket_id", "!=", False)],
            ["id:count_distinct"],
            ["helpdesk_ticket_id"],
        )
        ticket_count_mapping = dict(
            map(
                lambda group: (
                    group["helpdesk_ticket_id"][0],
                    group["helpdesk_ticket_id_count"],
                ),
                ticket_groups,
            )
        )
        for ticket in self:
            ticket.project_count = ticket_count_mapping.get(ticket.id, 0)

    def action_view_project(self):
        project_form_view = self.env.ref("project.edit_project")
        project_list_view = self.env.ref("project.view_project")
        action = {"type": "ir.actions.act_window", "res_model": "project.project"}

        if len(self.project_ids) == 1:
            action.update(
                res_id=self.project_ids[0].id, views=[(project_form_view.id, "form")]
            )
        else:
            action.update(
                domain=[("id", "in", self.project_ids.ids)],
                views=[(project_list_view.id, "tree"), (project_form_view.id, "form")],
                name=_("Projects From Ticket"),
            )
        return action

    def action_generate_project(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Create a Project"),
            "res_model": "helpdesk.create.project",
            "view_mode": "form",
            "target": "new",
            "context": {
                "use_project": True,
                "default_helpdesk_ticket_id": self.id,
                "default_user_id": False,
                "default_name": self.name,
            },
        }
