from odoo import api, fields, models


# Warranty texts
class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    warranty_text_ids = fields.One2many(
        comodel_name="warranty.policy.line",
        inverse_name="sale_order_id",
        string="Warranty / Notes",
        copy=False,
    )
    order_note = fields.Text()

    @api.onchange("warranty_text_ids")
    def _validate_warranty_text_ids(self):
        """Set warranty_text_ids.sale_order_id"""
        for record in self:
            if record.warranty_text_ids:
                if not record.warranty_text_ids.sale_order_id:
                    record.warranty_text_ids.sale_order_id = record.id

    def _prepare_invoice(self):
        result = super()._prepare_invoice()
        result.update({"invoice_note": self.order_note})
        return result
