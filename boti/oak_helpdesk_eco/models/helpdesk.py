from odoo import _, api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    use_plm = fields.Boolean("PLM ECOs", help="Convert tickets into PLM ECOs")


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    use_plm = fields.Boolean(related="team_id.use_plm")
    plm_eco_ids = fields.One2many(
        "mrp.eco",
        "helpdesk_ticket_id",
        string="ECOs",
        help="ECOs generated from this ticket",
        domain=[],
    )
    plm_eco_count = fields.Integer(compute="_compute_plm_eco_count")

    @api.depends("plm_eco_ids")
    def _compute_plm_eco_count(self):
        ticket_groups = self.env["mrp.eco"].read_group(
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
            ticket.plm_eco_count = ticket_count_mapping.get(ticket.id, 0)

    def action_view_plm_eco(self):
        plm_form_view = self.env.ref("mrp_plm.mrp_eco_view_form")
        plm_list_view = self.env.ref("mrp_plm.mrp_eco_view_tree")
        action = {"type": "ir.actions.act_window", "res_model": "mrp.eco"}

        if len(self.plm_eco_ids) == 1:
            action.update(
                res_id=self.plm_eco_ids[0].id, views=[(plm_form_view.id, "form")]
            )
        else:
            action.update(
                domain=[("id", "in", self.plm_eco_ids.ids)],
                views=[(plm_list_view.id, "tree"), (plm_form_view.id, "form")],
                name=_("ECOs from Tickets"),
            )
        return action

    def action_generate_plm_eco(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Create a PLM ECO"),
            "res_model": "helpdesk.create.eco",
            "view_mode": "form",
            "target": "new",
            "context": {
                "use_eco": True,
                "default_helpdesk_ticket_id": self.id,
                "default_user_id": False,
                "default_name": self.name,
            },
        }
