from odoo import fields, models


# Material types
class MrpEcoAddProduct(models.Model):
    _name = "mrp.eco.add.product"
    _description = "PLM-ECO additional products"

    eco_id = fields.Many2one("mrp.eco", "Parent ECO")
    name = fields.Char()
    product_tmpl_id = fields.Many2one("product.template", "Product")
    eco_product_state_id = fields.Many2one(
        related="product_tmpl_id.product_state_id", store=True, readonly=False
    )
    child_eco_id = fields.Many2one("mrp.eco", "Child ECO")
