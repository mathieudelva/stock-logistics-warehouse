# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CostAdjustmentDetail(models.Model):
    _name = "cost.adjustment.detail"
    _description = "Cost Adjustment Detail"
    _order = "cost_adjustment_id"

    cost_adjustment_id = fields.Many2one(
        "cost.adjustment",
        string="Cost Adjustment",
        check_company=True,
        index=True,
        required=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        check_company=True,
        index=True,
        required=True,
    )
    product_original_cost = fields.Float(
        string="Current Cost",
        readonly=True,
        default=0,
    )
    product_cost = fields.Float(
        string="Future Cost",
        readonly=True,
        states={"confirm": [("readonly", False)]},
        default=0,
    )
    difference_cost = fields.Float(
        string="Difference",
        compute="_compute_difference",
        help="Indicates the gap between the product's original cost and its new cost.",
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="cost_adjustment_id.company_id",
        index=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="company_id.currency_id",
    )

    @api.depends("product_cost", "product_original_cost")
    def _compute_difference(self):
        for line in self:
            line.difference_cost = line.product_cost - line.product_original_cost
