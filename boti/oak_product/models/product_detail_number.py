from odoo import fields, models


# Product Detail Number
class ProductDetailNumber(models.Model):
    _name = "product.detail.number"
    _description = "Product Grouping"
    _check_company_auto = True

    name = fields.Char(required="True")

    description = fields.Text()
