# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"

    @api.model
    def _send_email(self, options):
        """
        Send by mail the followup to the customer
        """
        partner = self.env["res.partner"].browse(options.get("partner_id"))
        non_blocked_amls = partner.unreconciled_aml_ids.filtered(
            lambda aml: not aml.blocked
        )
        if not non_blocked_amls:
            return True
        non_printed_invoices = partner.unpaid_invoices.filtered(
            lambda inv: not inv.message_main_attachment_id
        )
        if non_printed_invoices and partner.followup_level.join_invoices:
            raise UserError(
                _(
                    "You are trying to send a followup report to a partner for which "
                    "you didn't print all the invoices ({})"
                ).format(" ".join(non_printed_invoices.mapped("name")))
            )
        invoice_partner = self.env["res.partner"].browse(
            partner.address_get(["invoice"])["invoice"]
        )
        email = invoice_partner.email
        if email and email.strip():
            self = self.with_context(lang=partner.lang or self.env.user.lang)
            # When printing we need te replace the \n of the summary by <br /> tags
            body_html = self.with_context(print_mode=True, mail=True).get_html(options)
            body_html = body_html.replace(
                b"o_account_reports_edit_summary_pencil",
                b"o_account_reports_edit_summary_pencil d-none",
            )
            start_index = body_html.find(
                b"<span>", body_html.find(b'<div class="o_account_reports_summary">')
            )
            end_index = (
                start_index > -1 and body_html.find(b"</span>", start_index) or -1
            )
            if end_index > -1:
                replaced_msg = body_html[start_index:end_index].replace(b"\n", b"")
                body_html = (
                    body_html[:start_index] + replaced_msg + body_html[end_index:]
                )
            recipients_ids = partner.with_context(
                mail_post_autofollow=True, lang=partner.lang or self.env.user.lang
            )._message_get_default_recipients()
            followup_partner_ids = recipients_ids[partner.id].get("partner_ids")
            partner.with_context(
                mail_post_autofollow=True, lang=partner.lang or self.env.user.lang
            ).message_post(
                partner_ids=followup_partner_ids,
                body=body_html,
                subject=_(
                    "%(company)s Payment Reminder - %(customer)s",
                    company=self.env.company.name,
                    customer=partner.name,
                ),
                subtype_id=self.env.ref("mail.mt_note").id,
                model_description=_("payment reminder"),
                email_layout_xmlid="mail.mail_notification_light",
                attachment_ids=partner.followup_level.join_invoices
                and partner.unpaid_invoices.message_main_attachment_id.ids
                or [],
            )
            return True
        raise UserError(
            _(
                "Could not send mail to partner %s because it does not have any "
                "email address defined",
                partner.display_name,
            )
        )
