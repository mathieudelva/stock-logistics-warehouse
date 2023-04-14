from odoo import fields, models


class StockQuant(models.Model):
    """Stock Quant"""

    _inherit = "stock.quant"

    product_categ_id = fields.Many2one("product.category", store=True)

    standard_price = fields.Float(
        related="product_id.standard_price", store=True, readonly=True
    )
