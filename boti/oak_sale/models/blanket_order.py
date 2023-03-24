from odoo import fields, models


class BlanketOrderLine(models.Model):
    _inherit = "sale.blanket.order.line"

    partner_id = fields.Many2one(
        related="order_id.partner_id", string="Customer", store=True
    )
    validity_date = fields.Date(related="order_id.validity_date", store=True)
