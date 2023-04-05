from odoo import _, fields, models


class CreateSaleOrder(models.TransientModel):
    _name = "helpdesk.create.sale_order"
    _description = "Create a Sales Order"

    sale_order_helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Related ticket", required=True, readonly=True
    )
    company_id = fields.Many2one(related="sale_order_helpdesk_ticket_id.company_id")
    name = fields.Char(
        string="Order Reference", required=True, copy=False, readonly=True
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer Contact", required=True
    )
    partner_invoice_id = fields.Many2one(
        "res.partner", string="Customer Invoice Address", required=True
    )
    partner_shipping_id = fields.Many2one(
        "res.partner", string="Customer Delivery Address", required=True
    )
    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")
    partner_ref = fields.Char(string="Parent Account", store=True)

    sales_pool_id = fields.Many2one(
        "account.analytic.account", "Sales Type", help="Sales Type (Pool)"
    )
    sale_ordered_by_id = fields.Many2one("res.partner", string="Ordered By")

    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
    )

    sale_attention_to_note = fields.Text("Attention To Note", help="Attention to Note")

    def action_generate_sale_order(self):
        self.ensure_one()
        res = self.env["sale.order"].create(
            {
                "name": self.name,
                "partner_id": self.partner_id.id,
                "sale_order_helpdesk_ticket_id": self.sale_order_helpdesk_ticket_id.id,
                "partner_invoice_id": self.partner_invoice_id.id,
                "partner_shipping_id": self.partner_shipping_id.id,
                "pricelist_id": self.pricelist_id.id,
                "partner_ref": self.partner_ref,
                "company_id": self.company_id.id,
                "analytic_account_id": self.sales_pool_id.id,
                "sale_ordered_by_id": self.sale_ordered_by_id.id,
                "user_id": self.user_id.id,
                "note": self.sale_attention_to_note,
            }
        )

        self.sale_order_helpdesk_ticket_id.message_post(
            body=_(
                "Sales Quote Created <a href=# data-oe-model=sale.order data-oe-id=%(res_id)d>%(res_name)s</a>",
                res_id=res.id,
                res_name=res.name,
            )
        )
        res.message_post(
            body=_(
                "Created from Helpdesk Ticket "
                "<a href=# data-oe-model=helpdesk.ticket data-oe-id=%(helpdesk_ticket_id)d>%(helpdesk_ticket_name)s</a>",
                helpdesk_ticket_id=self.sale_order_helpdesk_ticket_id.id,
                helpdesk_ticket_name=self.sale_order_helpdesk_ticket_id.name,
            )
        )

        template_id = self.env.ref(
            "oak_helpdesk_sales_order.mail_template_sale_order_helpdesk"
        ).id
        template = self.env["mail.template"].browse(template_id)
        if self.partner_id.email:
            ctx = {
                "default_model": "sale.order",
                "default_res_id": self.sale_order_helpdesk_ticket_id.id,
                "default_use_template": bool(template_id),
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "mark_so_as_sent": True,
                "force_email": True,
                "sale_order_ref": res.name,
            }
            template.with_context(**ctx).send_mail(
                self.sale_order_helpdesk_ticket_id.id,
                force_send=True,
                email_layout_xmlid="mail.mail_notification_light",
            )
            self.sale_order_helpdesk_ticket_id.message_post(
                body=_("Email sent to customer")
            )
        else:
            self.sale_order_helpdesk_ticket_id.message_post(
                body=_("Unable to send email to customer!")
            )

        stage = self.env["helpdesk.stage"].search(
            [
                ("name", "=", _("Solved")),
                ("team_ids", "in", self.sale_order_helpdesk_ticket_id.team_id.id),
            ],
            limit=1,
        )
        if stage:
            self.sale_order_helpdesk_ticket_id.stage_id = stage.id

        return res

    def action_generate_and_view_sale_order(self):
        self.ensure_one()
        new_sale_order = self.action_generate_sale_order()
        return {
            "type": "ir.actions.act_window",
            "name": _("Sales Order from Tickets"),
            "res_model": "sale.order",
            "res_id": new_sale_order.id,
            "view_mode": "form",
            "view_id": self.env.ref("sale.view_order_form").id,
        }
