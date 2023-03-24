from odoo import fields, models


class product_template(models.Model):
    _inherit = "product.template"

    is_visit = fields.Boolean(
        "Visit Type Product",
        default=False,
        help="Set True if want to Invoice related visits only from SO.",
    )
