from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _visit_count(self):
        for rec in self:
            rec.visit_count = self.env["visit.visit"].search_count(
                [("partner_id", "=", rec.id)]
            )

    visit_count = fields.Integer(compute="_visit_count", readonly=True, string="Visits")

    def partner_visit_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "acs_visits.visit_visit_action"
        )
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {
            "default_partner_id": self.id,
        }
        return action
