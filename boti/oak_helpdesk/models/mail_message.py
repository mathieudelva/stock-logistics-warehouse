from odoo import api, fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    # external ref to simplify pre golive data synchronization
    external_ref = fields.Char()

    @api.model
    def create(self, vals):

        # Call the parent to create the message
        result = super(MailMessage, self).create(vals)

        # Public helpdesk communication is done from the helpdesk alias/team
        # Copy the reply-to address for public
        if (
            result.model == "helpdesk.ticket"
            and result.is_internal == 0
            and result.subtype_id.internal == 0
        ):
            # Copy over the From address
            result.email_from = result.reply_to

        # check for helpdesk ticket comment
        if (
            result.model == "helpdesk.ticket"
            and result.subtype_id.id == 1
            and (result.message_type == "comment" or result.message_type == "email")
        ):
            is_internal = False
            author_id = result.author_id.id
            if author_id:
                user_id = (
                    self.env["res.users"]
                    .sudo()
                    .search([("partner_id", "=", author_id)])
                )
                if user_id:
                    mail_user = self.env["res.users"].sudo().browse(user_id)
                    if mail_user.sudo().has_group("base.group_user"):
                        is_internal = True
            if result.res_id:
                ticket = self.env["helpdesk.ticket"].sudo().browse(result.res_id)
                if is_internal is True:
                    ticket.sudo().write({"kanban_state": "done"})
                else:
                    ticket.sudo().write({"kanban_state": "blocked"})

        return result
