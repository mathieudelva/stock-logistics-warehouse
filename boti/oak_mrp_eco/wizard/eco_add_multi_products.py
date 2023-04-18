# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EcoAddMultiProducts(models.TransientModel):
    _name = "eco.add.multi.product"
    _description = "Add Multiple Product to ECO"

    product_ids = fields.Many2many("product.product")

    global_state = fields.Many2one("product.state")

    def add_products(self):
        eco_mrp_obj = self.env["mrp.eco"]
        eco_add_products_obj = self.env["mrp.eco.add.product"]
        eco_id = 0
        eco_name = ""
        args = eco_mrp_obj.env.args
        argDict = args[2]
        if "eco_id" in argDict.keys():
            eco_id = argDict["eco_id"]
        if "eco_name" in argDict.keys():
            eco_name = argDict["eco_name"]
        if eco_id > 0:
            eco_mrp_obj.browse(eco_id)
            for rec in self:
                for product in rec.product_ids:
                    # add_product_id =
                    eco_add_products_obj.create(
                        [
                            {
                                "eco_id": eco_id,
                                "product_tmpl_id": product.product_tmpl_id.id,
                                "name": eco_name,
                                "eco_product_state_id": self.global_state.id,
                            }
                        ]
                    )
                    # add_product_id._set_default_restrictions()
