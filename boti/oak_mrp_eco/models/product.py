from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    eco_parent_count = fields.Integer(
        "Parent ECOs", compute="_compute_eco_parent_count"
    )

    def _compute_eco_parent_count(self):
        for p in self:
            pids = p.env["mrp.eco.add.product"].search([("product_tmpl_id", "=", p.id)])
            p.eco_parent_count = len(pids)
