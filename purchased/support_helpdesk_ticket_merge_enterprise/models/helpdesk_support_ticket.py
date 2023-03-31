# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    primary_ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Primary Merge Ticket",
    )
    merge_ticket_ids = fields.One2many(
        "helpdesk.ticket",
        "primary_ticket_id",
        string="Secondary Merge Tickets",
    )
    has_secondary = fields.Boolean(
        string="Has Child Tickets",
        default=False,
    )
    merge_reason = fields.Char()

    # @api.multi
    def show_secondary_ticket(self):
        self.ensure_one()
        secondary = self.search(
            [("primary_ticket_id", "=", self.id), ("active", "!=", True)]
        )
        # res = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        res = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree")
        res = res.sudo().read()[0]
        res["domain"] = str([("id", "in", secondary.ids), ("active", "!=", True)])
        return res
