from odoo import _, fields, models


class MrpEco(models.Model):
    _inherit = "mrp.eco"
    _description = "ECO additional products"

    eco_add_product_ids = fields.One2many(
        "mrp.eco.add.product", "eco_id", "Additional ECO Products", copy=True
    )

    eco_product_state_id = fields.Many2one(
        related="product_tmpl_id.product_state_id", store=True, readonly=False
    )

    def button_additional_products(self):
        eco_id = self.id
        eco_name = self.name
        return {
            "name": _("ECO Additional Products"),
            "type": "ir.actions.act_window",
            "res_model": "eco.add.multi.product",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"eco_id": eco_id, "eco_name": eco_name},
        }
