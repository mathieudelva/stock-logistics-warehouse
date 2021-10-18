# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class CostAdjustment(models.Model):
    _inherit = "cost.adjustment"

    def action_open_cost_adjustment_details(self):
        cost_detail_obj = self.env["cost.adjustment.detail"]
        details = cost_detail_obj.search([("cost_adjustment_id", "=", self.id)])
        details.unlink()
        for line in self.line_ids:
            self.get_product_bom_component(line.product_id)
            self.get_product_workcenter_operation(line.product_id)
        self._get_all_boms_details()
        self._create_all_operations_details()

        final_cost_lines_by_bom = cost_detail_obj.search(
            [("cost_adjustment_id", "=", self.id)]
        ).mapped("bom_id")

        final_cost_lines = cost_detail_obj.search(
            [("cost_adjustment_id", "=", self.id)]
        )

        for a in final_cost_lines_by_bom:
            total = sum(
                [
                    c.future_bom_cost
                    for c in final_cost_lines.filtered(lambda b: b.bom_id.id in a.ids)
                ]
            )
            parent_bom_detail = final_cost_lines.filtered(
                lambda exe: exe.product_id.id in a.product_id.ids
            )
            if not parent_bom_detail:
                parent_bom_detail = final_cost_lines.filtered(
                    lambda exe: exe.product_id.id
                    in a.product_tmpl_id.product_variant_ids.ids
                )
            parent_bom_detail.write({"product_cost": total})

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
                "stock_inventory_revaluation_wip.cost_adjustment_detail_mrp_view_tree_inherit"
            ).id,
        }
        return action

    def get_product_workcenter_operation(self, product):
        cost_driver_product_ids = self.env["product.product"].search(
            [
                ("activity_cost_ids.product_id", "=", product.id),
                ("is_cost_type", "=", True),
            ]
        )
        for cost_drive in cost_driver_product_ids:
            workcenter_id = self.env["mrp.workcenter"].search(
                [("analytic_product_id", "=", cost_drive.id)]
            )
            operation_ids = self.env["mrp.routing.workcenter"].search(
                [("workcenter_id", "=", workcenter_id.id), ("bom_id", "!=", None)]
            )
            for operation in operation_ids:
                self._create_cost_details_workcenter(cost_drive, operation)

    def _get_all_boms_details(self):
        for bom in (
            self.env["cost.adjustment.detail"]
            .search([("cost_adjustment_id", "=", self.id)])
            .mapped("bom_id")
        ):

            if bom.product_id:
                boms = self.env["mrp.bom"].search(
                    [("bom_line_ids.product_id", "in", bom.product_id.ids)]
                )
            else:
                product = self.env["product.product"].search(
                    [("product_tmpl_id", "=", bom.product_tmpl_id.id)], limit=1
                )
                boms = self.env["mrp.bom"].search(
                    [("bom_line_ids.product_id", "in", product.ids)]
                )
            for each in boms:
                self._create_all_bom_details(each)

    def _create_all_operations_details(self):
        for bom in (
            self.env["cost.adjustment.detail"]
            .search([("cost_adjustment_id", "=", self.id)])
            .mapped("bom_id")
        ):
            for operation in bom.operation_ids:
                for (
                    activity
                ) in operation.workcenter_id.analytic_product_id.activity_cost_ids:
                    if not self.env["cost.adjustment.detail"].search(
                        [
                            ("cost_adjustment_id", "=", self.id),
                            ("bom_id", "=", bom.id),
                            ("product_id", "=", activity.product_id.id),
                        ]
                    ):
                        self.env["cost.adjustment.detail"].create(
                            {
                                "product_id": activity.product_id.id,
                                "cost_adjustment_id": self.id,
                                # "bom_line_id": bom.id,
                                "bom_id": bom.id,
                                "quantity": activity.factor,
                                "product_original_cost": activity.product_id.standard_price,
                                "product_cost": activity.product_id.standard_price,
                            }
                        )

    def _create_all_bom_details(self, bom):
        for bom_line in bom.bom_line_ids:
            if not self.env["cost.adjustment.detail"].search(
                [
                    ("cost_adjustment_id", "=", self.id),
                    ("bom_id", "=", bom_line.bom_id.id),
                    ("product_id", "=", bom_line.product_id.id),
                ]
            ):
                self.env["cost.adjustment.detail"].create(
                    {
                        "product_id": bom_line.product_id.id,
                        "cost_adjustment_id": self.id,
                        "bom_line_id": bom_line.id,
                        "bom_id": bom_line.bom_id.id,
                        "quantity": bom_line.product_qty,
                        "product_original_cost": bom_line.product_id.standard_price,
                        "product_cost": bom_line.product_id.standard_price,
                    }
                )
                self._get_all_boms_details()

    def _create_cost_details_workcenter(self, cost_drive, operation):
        cost_line_obj = self.env["cost.adjustment.line"]
        for cost in cost_drive.activity_cost_ids:
            if not self.env["cost.adjustment.detail"].search(
                [
                    ("bom_id", "=", operation.bom_id.id),
                    ("operation_id", "=", operation.id),
                    ("product_id", "=", cost.product_id.id),
                    ("cost_adjustment_id", "=", self.id),
                ]
            ):

                prod_line = cost_line_obj.search(
                    [
                        ("cost_adjustment_id", "=", self.id),
                        ("product_id", "=", cost.product_id.id),
                    ]
                )
                future_cost = (
                    prod_line.product_cost
                    if prod_line.product_id.id == cost.product_id.id
                    else cost.product_id.standard_price
                )
                self.env["cost.adjustment.detail"].create(
                    {
                        "product_id": cost.product_id.id,
                        "cost_adjustment_id": self.id,
                        "bom_id": operation.bom_id.id,
                        "quantity": cost.factor,
                        "product_original_cost": prod_line.product_original_cost
                        if prod_line.product_id.id == cost.product_id.id
                        else cost.product_id.standard_price,
                        "product_cost": future_cost,
                        "operation_id": operation.id,
                    }
                )
        for bom_line in operation.bom_id.bom_line_ids:
            if not self.env["cost.adjustment.detail"].search(
                [
                    ("cost_adjustment_id", "=", self.id),
                    ("bom_id", "=", operation.bom_id.id),
                    ("product_id", "=", bom_line.product_id.id),
                ]
            ):
                self.env["cost.adjustment.detail"].create(
                    {
                        "product_id": bom_line.product_id.id,
                        "cost_adjustment_id": self.id,
                        "bom_line_id": bom_line.id,
                        "bom_id": operation.bom_id.id,
                        "quantity": bom_line.product_qty,
                        "product_original_cost": bom_line.product_id.standard_price,
                        "product_cost": bom_line.product_id.standard_price,
                    }
                )

    def action_post(self):
        res = super().action_post()
        wc_ids = (
            self.env["cost.adjustment.detail"]
            .search([("cost_adjustment_id", "=", self.id)])
            .mapped("operation_id")
        )
        for wc in wc_ids:
            wc.workcenter_id.analytic_product_id.sudo().onchange_for_standard_price()

        bom_ids = (
            self.env["cost.adjustment.detail"]
            .search([("cost_adjustment_id", "=", self.id)])
            .mapped("bom_id")
        )
        for bom in bom_ids:
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
