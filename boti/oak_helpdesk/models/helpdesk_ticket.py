from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    activity_user_id = fields.Many2one(
        related="activity_ids.user_id", string="Activity User", readonly=True
    )

    activity_due_date = fields.Date(
        related="activity_ids.date_deadline", string="Activity Due", readonly=True
    )

    # add tracking to ticket_type
    ticket_type_id = fields.Many2one("helpdesk.ticket.type", tracking=True)
