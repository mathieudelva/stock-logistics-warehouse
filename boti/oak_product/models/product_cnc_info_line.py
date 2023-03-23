from odoo import fields, models


class ProductCNCInfoLine(models.Model):
    _name = "product.cnc.info.line"
    _description = "Product CNC Info"
    _order = "name"
    _check_company_auto = True

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )

    sequence = fields.Integer(default=10)

    name = fields.Char(string="Program")
    cnc_length = fields.Float(string="CNC - Length")
    cnc_diameter = fields.Float(string="CNC - Diameter")
    workcenter_id = fields.Many2one("mrp.workcenter", "Work Center")
    department_id = fields.Many2one(
        related="workcenter_id.department_id", readonly=True
    )
