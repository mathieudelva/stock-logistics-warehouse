from odoo import fields, models


# Sales Warranty Policy
class WarrantyPolicy(models.Model):
    _name = "warranty.policy"
    _description = "Sales Warranty Disclaimer Text"
    _check_company_auto = True
    _order = "sequence, name"

    sequence = fields.Integer()

    name = fields.Char(string="Title", required="True")

    description = fields.Text(string="Warranty Disclaimer Text", required="True")

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)


class WarrantyPolicyLine(models.Model):
    _name = "warranty.policy.line"
    _description = "Warranty Paragraphs"
    _order = "sequence, sale_order_id"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order", string="Order", ondelete="cascade"
    )

    warranty_text_id = fields.Many2one("warranty.policy", "Warranty / Notes")

    sequence = fields.Integer(default=10)
