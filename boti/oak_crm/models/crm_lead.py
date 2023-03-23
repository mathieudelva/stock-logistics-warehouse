from odoo import fields, models


# Inheriting the sale.order and adding new fields
class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = "crm.lead"

    product_type_id = fields.Many2one(
        "product.family", "Machine Type", help="Sales Machine Types"
    )

    product_type_category_id = fields.Many2one(
        comodel_name="product.family.category",
        related="product_type_id.product_type_category_id",
        string="Machine Type Category",
        store=True,
        help="Parent Machine Type Category",
    )
