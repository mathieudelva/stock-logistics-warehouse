from odoo import fields, models


# Imported Legacy BoM
class ProductLegacyUOM(models.Model):
    _name = "product.legacy.uom"
    _description = "Legacy UOM Mapping"

    legacy_uom = fields.Char(string="Legacy UOM")
    odoo_uom = fields.Many2one("uom.uom")
