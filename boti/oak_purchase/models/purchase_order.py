from odoo import _, api, exceptions, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vendor_ref = fields.Char(
        string="Account Number", store=True, related="partner_id.ref"
    )

    date_approve = fields.Datetime(
        "PO Confirmation Date", readonly=1, index=True, copy=False
    )

    def action_purchase_confirm_send(self):
        self.ensure_one()
        template_id = self.env.ref(
            "oak_purchase.mail_template_purchase_confirmation", raise_if_not_found=False
        )

        lang = self.env.context.get("lang")
        if template_id.lang:
            lang = template_id._render_lang(self.ids)[self.id]
        ctx = {
            "default_model": "purchase.order",
            "active_model": "purchase.order",
            "default_res_id": self.ids[0],
            "default_use_template": bool(template_id),
            "default_template_id": template_id.id,
            "default_composition_mode": "comment",
            "mark_so_as_sent": True,
            "custom_layout": "mail.mail_notification_paynow",
            "force_email": True,
            "model_description": _("Purchase Order"),
        }
        self = self.with_context(lang=lang)
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

    @api.onchange("receipt_reminder_email")
    def _onchange_receipt_reminder_email(self):
        for po in self:
            if po.receipt_reminder_email and po.partner_id and not po.partner_id.email:
                raise exceptions.UserError(
                    _(
                        "Vendor does not have an email address. "
                        "Please update the Vendor's email address."
                    )
                )
