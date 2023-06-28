# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_lock_cost = fields.Boolean(
        compute="_compute_allow_lock_cost", string="Allow Lock Cost Price"
    )
    standard_price = fields.Float("Cost (Active)")
    proposed_cost_ignore_bom = fields.Boolean(
        help="This product is preferably purchased, so don't use BoM when rolling up cost"
    )

    def _compute_allow_lock_cost(self):
        for product in self:
            product.allow_lock_cost = self.env.user.company_id.lock_cost_products


class ProductProduct(models.Model):
    _inherit = "product.product"

    proposed_cost_ignore_bom = fields.Boolean()

    def _get_rollup_cost(self, adjustment_id, computed_products):
        if computed_products:
            if self.id not in computed_products.keys():
                if self.type == 'product' and not self.standard_price:
                    adjustment_id.message_post(
                        body=_(
                            "Standard Cost on product %(item)s is 0.0",
                            item=self.default_code,
                        )
                    )
                cost = self.standard_price
            else:
                if computed_products[self.id] > 0:
                    cost = computed_products[self.id]
                else:
                    cost = self.proposed_cost or self.standard_price
        else:
            cost = self.proposed_cost or self.standard_price
        return cost

    def calculate_proposed_cost(self, computed_products=None, adjustment_id = False):
        DecimalPrecision = self.env["decimal.precision"]
        
        # initial call
        if computed_products==None:
            computed_products={}

        if computed_products == {} and adjustment_id and not adjustment_id.line_ids:
            computed_products = dict.fromkeys(adjustment_id.mapped('product_ids').ids, -1)
            for product in adjustment_id.product_ids:
                if not product.bom_ids:
                    computed_products[product.id] = product._get_rollup_cost(adjustment_id, computed_products)

        # recursive call
        else:
            for line in adjustment_id.line_ids:
                if line.product_id.id not in computed_products.keys():
                    computed_products[line.product_id.id] = line.product_id.proposed_cost

        products = self.filtered(
            lambda x: (x.bom_ids or x.is_cost_type) and not x.proposed_cost_ignore_bom
        )

        # get cost for lowest level products
        if self - products:
            for product in (self-products):
                if product.id not in computed_products.keys():
                    computed_products[product.id] = product._get_rollup_cost(adjustment_id, computed_products)

        for product in products:
            # cost type services
            if product.is_cost_type:
                if product.activity_cost_ids:
                    total = total_uom = 0
                    for act_cost_rule in product.activity_cost_ids:
                        line_total = act_cost_rule.product_id._get_rollup_cost(adjustment_id, computed_products)
                        computed_products[act_cost_rule.product_id.id] = line_total
                        total_uom += line_total * act_cost_rule.factor

                    # Set proposed cost if different from the actual cost
                    product.proposed_cost = total_uom
                    computed_products[product.id] = total_uom
            # products
            else:
                bom = self.env["mrp.bom"]._bom_find(product)[product]
                # First recompute "Proposed Cost" for the BoM components that also have a BoM
                components = bom.bom_line_ids.product_id
                components = components.filtered(
                    lambda pr: pr.id not in [*computed_products] or computed_products[pr.id] == -1
                )

                intermediates = components.calculate_proposed_cost(computed_products=computed_products,adjustment_id=adjustment_id)

                # Add the costs for all Components and Operations,
                # using the Active Cost when available, or the Proposed Cost otherwise
                cost_components = sum(
                    x.product_id.uom_id._compute_price(
                        computed_products[x.product_id.id], x.product_uom_id
                    )
                    * x.product_qty
                    for x in bom.bom_line_ids
                )
                op_products = bom.operation_ids.mapped("workcenter_id").mapped(
                    "analytic_product_id"
                )
                op_products = op_products.filtered(
                    lambda pr: pr.id not in [*computed_products] or computed_products[pr.id] == -1
                )

                op_cost_types = op_products.calculate_proposed_cost(computed_products=computed_products, adjustment_id=adjustment_id)

                cost_operations = sum(
                    x.workcenter_id.analytic_product_id._get_rollup_cost(adjustment_id, computed_products)
                    * (x.time_cycle / 60)
                    for x in bom.operation_ids
                )
                total = cost_components + cost_operations
                total_uom = bom.product_uom_id._compute_price(
                    total / bom.product_qty, product.uom_id
                )

                # Set proposed cost if different from the actual cost
                product.proposed_cost = total_uom
                computed_products[product.id] = total_uom

        return computed_products

    def _get_bom_structure_products(self):
        BOM = self.env["mrp.bom"]
        assemblies = self.filtered(
            lambda x: x.bom_ids and not x.proposed_cost_ignore_bom
        )
        bom_structure = assemblies
        for product in assemblies:
            bom = BOM._bom_find(product)[product]
            if bom and bom.product_tmpl_id:
                components = bom.bom_line_ids.product_id
                bom_structure |= components._get_bom_structure_products()
        return bom_structure

    def update_bom_version(self):
        bom_line_obj = self.env["mrp.bom.line"]
        bom_obj = self.env["mrp.bom"]
        no_of_bom_version = self.env.company.no_of_bom_version
        for product in self:
            bom_ids = product.bom_ids[0]
            for bom_id in bom_ids:
                version_boms = bom_obj.search(
                    [
                        ("product_tmpl_id", "=", bom_id.product_tmpl_id.id),
                        ("active", "=", False),
                        ("cost_roll_up_version", "=", True)
                    ],
                    order="id ASC",
                )
                version_boms.filtered(lambda l: l.active_ref_bom == True).write({"active_ref_bom": False})
                if version_boms and len(version_boms) >= no_of_bom_version:
                    limit = (len(version_boms) - no_of_bom_version)
                    unlink_boms = version_boms[0:limit+1]
                    unlink_boms.unlink()
                new_bom = bom_id.copy(
                    {
                        "active": False,
                        "active_ref_bom": True,
                        "cost_roll_up_version": True,
                    }
                )
                for line in new_bom.bom_line_ids:
                    line.write({"unit_cost": line.product_id.standard_price})

                for operatine in new_bom.operation_ids.filtered(
                    lambda l: l.workcenter_id.analytic_product_id.activity_cost_ids
                ):
                    activity_cost_ids = []
                    for (
                        activity
                    ) in operatine.workcenter_id.analytic_product_id.activity_cost_ids:
                        activity_cost_ids.append(
                            (
                                0,
                                0,
                                {
                                    "analytic_product_id": operatine.workcenter_id.analytic_product_id.id,
                                    "product_id": activity.product_id.id,
                                    "standard_price": activity.standard_price,
                                    "factor": activity.factor,
                                },
                            )
                        )
                    if activity_cost_ids:
                        operatine.write({"operation_info_ids": activity_cost_ids})
