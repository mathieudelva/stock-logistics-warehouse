from odoo import _, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    mrp_workcenter_team_id = fields.Many2many(
        "mrp.workcenter.team", string="MRP WorkCenter Team"
    )


class MrpWorkcenterTeam(models.Model):
    _name = "mrp.workcenter.team"
    _description = "MRP WorkCenter Teams"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Maintenance Team", required=True)
    active = fields.Boolean("Active", default=True)
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company, readonly=True
    )
    resource_calendar_id = fields.Many2one(
        "resource.calendar",
        "Working Time",
        required=True,
        default=lambda self: self.env.company.resource_calendar_id.id,
    )
    user_id = fields.Many2one("res.users", "Team Leader")
    member_ids = fields.Many2many(
        "res.users",
        "mrp_workcenter_team_user_rel",
        "mrp_workcenter_team_id",
        "uid",
        string="Team Members",
        copy=False,
    )
    mrp_wc_count = fields.Integer("Work Centers", compute="_mrp_wc_count")

    def _mrp_wc_count(self):
        for team in self:
            team.mrp_wc_count = self.env["mrp.workcenter"].search_count(
                [("mrp_workcenter_team_id", "=", team.id)]
            )

    def action_view_workcenter(self):
        context = {
            "search_default_mrp_workcenter_team_id": [self.id],
            "default_mrp_workcenter_team_id": self.id,
        }
        return {
            "domain": "[('mrp_workcenter_team_id','in',["
            + ",".join(map(str, self.ids))
            + "])]",
            "context": context,
            "name": _("Work Centers"),
            "view_mode": "tree,form",
            "res_model": "mrp.workcenter",
            "type": "ir.actions.act_window",
            "target": "current",
        }
