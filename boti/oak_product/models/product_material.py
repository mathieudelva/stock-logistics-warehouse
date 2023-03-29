from odoo import fields, models


# Material types
class ProductMaterial(models.Model):
    _name = "product.material"
    _description = "Materials"
    _check_company_auto = True

    name = fields.Char(string="Material ID", required="True")

    description = fields.Text()
