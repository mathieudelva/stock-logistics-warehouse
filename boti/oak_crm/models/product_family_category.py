from odoo import fields, models


# Sales Product Types/Families
class ProductFamilyCategory(models.Model):
    _name = "product.family.category"
    _description = "Sales Machine Type Categories"
    _check_company_auto = True

    name = fields.Char(string="Category", required="True")

    description = fields.Char()
