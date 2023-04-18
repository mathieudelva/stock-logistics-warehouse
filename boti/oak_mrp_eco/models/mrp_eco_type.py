from odoo import models


class MrpEcoType(models.Model):
    _inherit = "mrp.eco.type"

    def get_mrp_eco_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).sudo().read()[0]
        if self:
            action["display_name"] = self.display_name
        return action

    def get_plm_title_in_menu(self):
        return self.get_mrp_eco_action("mrp_plm.mrp_eco_action")
