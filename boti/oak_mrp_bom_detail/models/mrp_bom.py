from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    detail_id = fields.Many2one(
        related="product_tmpl_id.detail_number_id", store=True, readonly=True
    )


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    detail_id = fields.Many2one(
        related="product_id.product_tmpl_id.detail_number_id", readonly=True
    )
