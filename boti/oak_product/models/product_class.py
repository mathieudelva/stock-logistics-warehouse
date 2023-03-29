from odoo import fields, models


# Material types
class ProductClass(models.Model):
    _name = "product.class"
    _description = "Classification"
    _check_company_auto = True

    name = fields.Char(required="True")

    description = fields.Text()
