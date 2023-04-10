from odoo import _, api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    use_sale_order = fields.Boolean(
        "Use Sales Order", help="Convert tickets into a Sales Order"
    )


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    use_sale_order = fields.Boolean(related="team_id.use_sale_order")
    sales_helpdesk_orders_ids = fields.One2many(
        "sale.order",
        "sale_order_helpdesk_ticket_id",
        string="Sales Orders",
        help="Sales Order generated from this ticket",
    )
    sale_helpdesk_order_count = fields.Integer(
        compute="_compute_sale_helpdesk_order_count"
    )

    @api.depends("sales_helpdesk_orders_ids")
    def _compute_sale_helpdesk_order_count(self):
        ticket_groups = self.env["sale.order"].read_group(
            [("sale_order_helpdesk_ticket_id", "!=", False)],
            ["id:count_distinct"],
            ["sale_order_helpdesk_ticket_id"],
        )
        ticket_count_mapping = dict(
            map(
                lambda group: (
                    group["sale_order_helpdesk_ticket_id"][0],
                    group["sale_order_helpdesk_ticket_id_count"],
                ),
                ticket_groups,
            )
        )
        for ticket in self:
            ticket.sale_helpdesk_order_count = ticket_count_mapping.get(ticket.id, 0)

    def action_view_sale_order(self):
        sales_orders_form_view = self.env.ref("sale.view_order_form")
        sales_orders_list_view = self.env.ref("sale.view_order_tree")
        action = {"type": "ir.actions.act_window", "res_model": "sale.order"}

        if len(self.sales_helpdesk_orders_ids) == 1:
            action.update(
                res_id=self.sales_helpdesk_orders_ids[0].id,
                views=[(sales_orders_form_view.id, "form")],
            )
        else:
            action.update(
                domain=[("id", "in", self.sales_helpdesk_orders_ids.ids)],
                views=[
                    (sales_orders_list_view.id, "tree"),
                    (sales_orders_form_view.id, "form"),
                ],
                name=_("Sales Orders from Ticket"),
            )
        return action

    def action_generate_sale_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Create a new sale order"),
            "res_model": "helpdesk.create.sale_order",
            "view_mode": "form",
            "target": "new",
            "context": {
                "use_sale_order": True,
                "default_sale_order_helpdesk_ticket_id": self.id,
                "default_partner_id": self.partner_id.id,
                "default_partner_invoice_id": self.partner_id.address_get(
                    ["delivery", "invoice"]
                )["invoice"],
                "default_partner_shipping_id": self.partner_id.address_get(
                    ["delivery", "invoice"]
                )["delivery"],
                "default_pricelist_id": self.partner_id.property_product_pricelist.id,
                "default_name": self.env["ir.sequence"].next_by_code("sale.order"),
                "default_partner_ref": self.partner_id.ref,
                "default_sale_ordered_by_id": self.partner_id.id,
                "default_user_id": self.partner_id.user_id.id,
            },
        }
