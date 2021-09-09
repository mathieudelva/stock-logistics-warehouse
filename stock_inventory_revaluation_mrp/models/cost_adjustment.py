# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models

bom_prods = []


class CostAdjustment(models.Model):
    _inherit = "cost.adjustment"

    def action_open_cost_adjustment_details(self):
        details = self.env["cost.adjustment.detail"].search(
            [("cost_adjustment_id", "=", self.id)]
        )
        details.unlink()
        for product in self.product_ids:
            self.get_product_bom_component(product)
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Cost Adjustment Detail"),
            "res_model": "cost.adjustment.detail",
            "context": {
                "default_is_editable": False,
                "default_cost_adjustment_id": self.id,
                "default_company_id": self.company_id.id,
                "search_default_group_by_bom_id": 1,
            },
            "domain": [("cost_adjustment_id", "=", self.id)],
            "view_id": self.env.ref(
                "stock_inventory_revaluation_mrp.cost_adjustment_detail_mrp_view_tree"
            ).id,
            # "views": [[False, "list"]],
        }
        return action

    def get_product_bom_component(self, product=None):
        bom_obj = self.env["mrp.bom"]
        if product:
            boms = bom_obj.search([("bom_line_ids.product_id", "in", product.ids)])
            if boms:
                self._create_cost_details(boms, product)
            bom_prods.append(product.id)
            for bom in boms:
                self.get_product_bom_component(bom.product_id)

    def _create_cost_details(self, boms, product):
        cost_detail_obj = self.env["cost.adjustment.detail"]
        cost_line_obj = self.env["cost.adjustment.line"]
        for bom in boms.bom_line_ids:
            # if not cost_detail_obj.search([("product_id","=",product.id),
            # ("cost_adjustment_id","=",self.id),
            # ("parent_product_id","=",bom.product_id.id)]):
            if not cost_detail_obj.search(
                [
                    ("bom_line_id", "=", bom.id),
                    ("cost_adjustment_id", "=", self.id),
                    ("bom_id", "=", bom.bom_id.id),
                    ("product_id", "=", bom.product_id.id),
                ]
            ):
                prod_line = cost_line_obj.search(
                    [
                        ("cost_adjustment_id", "=", self.id),
                        ("product_id", "=", product.id),
                    ]
                )

                cost_detail_obj.create(
                    {
                        "product_id": bom.product_id.id,
                        "cost_adjustment_id": self.id,
                        "bom_line_id": bom.id,
                        "product_original_cost": prod_line.product_original_cost
                        if prod_line.product_id.id == bom.product_id.id
                        else bom.product_id.standard_price,
                        "product_cost": prod_line.product_cost
                        if prod_line.product_id.id == bom.product_id.id
                        else bom.product_id.standard_price,
                    }
                )
        return True
