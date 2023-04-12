from odoo import fields, models


class StockQuant(models.Model):
    """Stock Quant"""

    _inherit = "stock.quant"

    categ_id = fields.Many2one(
        "product.category", related="product_id.categ_id", store=True
    )

    standard_price = fields.Float(
        related="product_id.standard_price", store=True, readonly=True
    )
