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

    def _notify_get_groups(self, msg_vals=None):
        # Original method is from portal.mixin, and is extended by helpdesk.ticket
        groups = super(HelpdeskTicket, self)._notify_get_groups(msg_vals=msg_vals)
        # All mail notified followers will see the Ticket link using the access token
        self.ensure_one()
        new_groups = []
        for group_name, _group_method, group_data in groups:
            new_group = (group_name, _group_method, group_data)
            if group_name == "portal_customer":
                group_data["has_button_access"] = True
                new_group = (
                    group_name,
                    lambda pdata: pdata["id"] in self.message_partner_ids.ids,
                    group_data,
                )
            new_groups.append(new_group)
        return new_groups
