from odoo import fields, models


# visit assessments
class VisitProductStatus(models.Model):
    _name = "visit.product.status"
    _description = "Equipment Use Status"
    _check_company_auto = True

    name = fields.Char(
        name="Equipment Status", required="True", help="Using Our Equipment Status"
    )
    description = fields.Text(name="Description")
