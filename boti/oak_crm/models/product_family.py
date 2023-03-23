from odoo import fields, models


# Sales Product Types/Families
class ProductFamily(models.Model):
    _name = "product.family"
    _description = "Sales Machine Types"
    _check_company_auto = True

    name = fields.Char(string="Type", required="True")

    description = fields.Char()

    product_type_category_id = fields.Many2one(
        "product.family.category",
        "Product Type Category",
        help="Sales Machine Type Category",
    )
