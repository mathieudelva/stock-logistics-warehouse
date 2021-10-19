# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class CostAdjustment(models.Model):
    _inherit = "cost.adjustment"

    def action_open_cost_adjustment_details(self):
        details = self.env["cost.adjustment.detail"].search(
            [("cost_adjustment_id", "=", self.id)]
        )
        details.unlink()
        for line in self.line_ids:
            self.get_product_bom_component(line.product_id)
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
        }
        return action

    def get_product_bom_component(self, product=None):
        bom_obj = self.env["mrp.bom"]
        if product:
            boms = bom_obj.search([("bom_line_ids.product_id", "in", product.ids)])
            if boms:
                self._create_cost_details(boms, product)
            for bom in boms:
                if bom.product_id:
                    self.get_product_bom_component(bom.product_id)
                else:
                    product = self.env["product.product"].search(
                        [("product_tmpl_id", "=", bom.product_tmpl_id.id)], limit=1
                    )
                    self.get_product_bom_component(product)

    def _create_cost_details(self, boms, product):
        cost_detail_obj = self.env["cost.adjustment.detail"]
        cost_line_obj = self.env["cost.adjustment.line"]
        for bom in boms.bom_line_ids:

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
                        ("product_id", "=", bom.product_id.id),
                    ]
                )

                parent_bom = cost_detail_obj.search(
                    [
                        "|",
                        ("bom_id.product_id", "=", bom.product_id.id),
                        (
                            "bom_id.product_tmpl_id",
                            "=",
                            bom.product_id.product_tmpl_id.id,
                        ),
                        ("cost_adjustment_id", "=", self.id),
                    ]
                )
                if parent_bom:
                    future_cost = sum([a.future_bom_cost for a in parent_bom])
                else:
                    future_cost = (
                        prod_line.product_cost
                        if prod_line.product_id.id == bom.product_id.id
                        else bom.product_id.standard_price
                    )

                cost_detail_obj.create(
                    {
                        "product_id": bom.product_id.id,
                        "cost_adjustment_id": self.id,
                        "bom_line_id": bom.id,
                        "bom_id": bom.bom_id.id,
                        "quantity": bom.product_qty,
                        "product_original_cost": prod_line.product_original_cost
                        if prod_line.product_id.id == bom.product_id.id
                        else bom.product_id.standard_price,
                        "product_cost": future_cost,
                    }
                )
        return True

    def action_post(self):
        res = super().action_post()
        for line in self.line_ids:
            for bom in line.product_id.bom_line_ids.mapped("bom_id"):
                if bom.product_id:
                    bom.product_id.sudo().button_bom_cost()
                else:
                    bom.product_tmpl_id.sudo().button_bom_cost()
                for parent_bom in (
                    bom.product_id.bom_line_ids.mapped("bom_id")
                    if bom.product_id
                    else bom.product_tmpl_id.bom_line_ids.mapped("bom_id")
                ):
                    if parent_bom.product_id:
                        parent_bom.product_id.sudo().button_bom_cost()
                    else:
                        parent_bom.product_tmpl_id.sudo().button_bom_cost()
        return res
