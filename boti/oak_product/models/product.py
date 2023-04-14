from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template"
    _order = "name"

    default_code = fields.Char(tracking=True)

    detail_number_id = fields.Many2one(
        "product.detail.number", "Detail Number", help="Product Detail Numbers"
    )

    generic_name_id = fields.Many2one(
        "product.generic.name", "Generic name", help="Product Generic Names"
    )

    eng_note = fields.Text(string="Engineering notes")

    class_id = fields.Many2one(
        "product.class", "Class", help="Product Engineer Classification"
    )

    material_id = fields.Many2one(
        "product.material", "Material", help="Product material"
    )

    cnc_info_line = fields.One2many(
        comodel_name="product.cnc.info.line",
        inverse_name="product_tmpl_id",
        string="CNC Program Info",
        copy=False,
    )

    categ_id = fields.Many2one(tracking=True)
    allow_negative_stock = fields.Boolean(tracking=True)
    company_id = fields.Many2one(tracking=True)
    uom_id = fields.Many2one(tracking=True)
    uom_po_id = fields.Many2one(tracking=True)
    proposed_cost = fields.Float(tracking=True)


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(tracking=True)
    default_code = fields.Char(tracking=True)
    proposed_cost = fields.Float(tracking=True)
