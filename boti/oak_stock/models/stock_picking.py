from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sale_tag_ids = fields.Many2many(related="sale_id.tag_ids")
