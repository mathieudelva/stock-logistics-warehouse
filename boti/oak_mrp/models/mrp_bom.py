from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    detail_id = fields.Many2one(
        related="product_tmpl_id.detail_number_id", store=True, readonly=True
    )


# Inheriting the MrpBomLine Model and adding new fields
class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    # external ref to simplify pre golive BoM line syncronization
    external_ref = fields.Char("External Ref #")

    detail_id = fields.Many2one(
        related="product_id.product_tmpl_id.detail_number_id", readonly=True
    )
