from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Helpdesk Ticket",
        help="Ticket this Sales Order was generated from",
        readonly=True,
    )

    def action_view_sale_order_ticket(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "form",
            "res_id": self.sale_order_helpdesk_ticket_id.id,
        }
