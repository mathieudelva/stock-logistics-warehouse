# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class CostAdjustment(models.Model):
    _inherit = "cost.adjustment"

    def action_open_cost_adjustment_details(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Cost Adjustment Details"),
            "res_model": "cost.adjustment.detail",
            "context": {
                "default_is_editable": False,
                "default_cost_adjustment_id": self.id,
                "default_company_id": self.company_id.id,
            },
            "domain": [("cost_adjustment_id", "=", self.id)],
            "view_id": self.env.ref(
                "stock_inventory_revaluation_mrp.cost_adjustment_detail_mrp_view_tree"
            ).id,
        }
        return action
