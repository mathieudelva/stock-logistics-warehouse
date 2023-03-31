from odoo import _, fields, models


class CreateProject(models.TransientModel):
    _name = "helpdesk.create.project"
    _description = "Create a Project"

    helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Related ticket", required=True
    )
    company_id = fields.Many2one(related="helpdesk_ticket_id.company_id")
    name = fields.Char("Title", required=True)
    project_tmpl_id = fields.Many2one(
        "project.project",
        string="Project Template",
        help="Optional Project Template to use",
        required=False,
        # Polish notation is ... stupid
        # this is is_template=true AND (company_id=false OR company_id=company_id)
        domain="['&', ('is_template', '=', True), \
            '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    note = fields.Html(related="helpdesk_ticket_id.description")

    def action_generate_project(self):
        self.ensure_one()

        if self.project_tmpl_id.id:

            project = self.project_tmpl_id.copy(
                default={
                    "name": self.name
                    + " for Helpdesk #"
                    + str(self.helpdesk_ticket_id.id),
                    "active": True,
                    "alias_name": False,
                    "helpdesk_ticket_id": self.helpdesk_ticket_id.id,
                    "description": self.note,
                    "company_id": self.company_id.id,
                }
            )

            # populate end dates on taskes
            # like code from create_from_template in project_template code
            for new_task_record in project.task_ids:
                for old_task_record in project.task_ids:
                    if new_task_record.name == old_task_record.name:
                        new_task_record.date_end = old_task_record.date_end

        else:
            project = self.env["project.project"].create(
                {
                    "name": self.name
                    + " for Helpdesk #"
                    + str(self.helpdesk_ticket_id.id),
                    "helpdesk_ticket_id": self.helpdesk_ticket_id.id,
                    "description": self.note,
                    "company_id": self.company_id.id,
                }
            )

        return project

    def action_generate_and_view_project(self):
        self.ensure_one()
        new_project = self.action_generate_project()
        return {
            "type": "ir.actions.act_window",
            "name": _("Project from Ticket"),
            "res_model": "project.project",
            "res_id": new_project.id,
            "view_mode": "form",
            "view_type": "form",
            "view_id": self.env.ref("project.edit_project").id,
        }
