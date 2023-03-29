from odoo import fields, models


# Product Generic Name
class ProductGenericName(models.Model):
    _name = "product.generic.name"
    _description = "Product Grouping by Generic Name"
    _check_company_auto = True

    name = fields.Char(required="True")

    description = fields.Text()
