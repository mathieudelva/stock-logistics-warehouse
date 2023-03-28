from odoo import fields, models


class ProductLegacyCNCLine(models.Model):
    _name = "product.legacy.cnc.line"
    _description = "Product Legacy CNC Line"
    _order = "name"
    _check_company_auto = True

    product_legacy_id = fields.Many2one(
        comodel_name="product.legacy",
        name="Product Legacy Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )

    sequence = fields.Integer(name="Sequence", default=10)

    name = fields.Char(name="Legacy Program")
    cnc_length = fields.Float(name="CNC - Length")
    cnc_diameter = fields.Float(name="CNC - Diameter")
    workcenter_id = fields.Many2one("mrp.workcenter", "Work Center")
