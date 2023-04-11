from odoo import api, fields, models


# Inheriting the sale.order and adding new fields
class SaleOrder(models.Model):
    _inherit = "sale.order"

    promise_date = fields.Datetime(index=True)

    partner_ref = fields.Char(
        string="Account Number",
        store=True,
        related="partner_id.commercial_partner_id.ref",
    )

    shiprefemail = fields.Char(
        string="Delivery Email", related="partner_shipping_id.email"
    )

    shipref = fields.Char(string="Delivery Ref", related="partner_shipping_id.ref")

    expedite = fields.Boolean()

    sales_rep_id = fields.Many2one(
        "res.partner", "External Sales Rep", help="External Sales Representative"
    )

    sales_rep_second_id = fields.Many2one(
        "res.partner",
        "Secondary External Sales Rep",
        help="External Sales Representative",
    )

    sale_leadtime_message_id = fields.Many2one(
        "sale.leadtime.message",
        "Lead Time Message ID",
        help="Quotation lead time messages",
        tracking=True,
    )

    sale_attention_to_note = fields.Text(
        "Attention To Note", help="Attention to Note", tracking=True
    )

    sale_attention_to_id = fields.Many2one(
        "res.partner", "Attention To", help="Attention to Contact", tracking=True
    )

    sale_ordered_by_id = fields.Many2one(
        "res.partner", "Ordered By", help="Ordered by Contact", tracking=True
    )

    @api.onchange("sale_ordered_by_id")
    def _onchange_sale_ordered_by_id(self):
        """Set the partner_id"""
        if not (
            self.partner_id == self.sale_ordered_by_id
            or self.partner_id == self.sale_ordered_by_id.commercial_partner_id
        ):
            # set partner_id to ordered by or commercial_partner_id
            # need to know which (maybe we need to make a parameter choice)
            self.partner_id = self.sale_ordered_by_id.commercial_partner_id
            # self.partner_id = self.sale_ordered_by_id

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.partner_ref = self.partner_id.commercial_partner_id.ref
        self.sales_rep_id = self.partner_id.extrep_id
        if not self.partner_id.property_delivery_carrier_id:
            self.carrier_id = self.partner_id.parent_id.property_delivery_carrier_id
        else:
            self.carrier_id = self.partner_id.property_delivery_carrier_id

        if self.partner_id.type in ["contact", "other"]:
            self.sale_ordered_by_id = self.partner_id

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if not self.partner_id.sale_incoterm_id:
            self.incoterm = self.partner_id.parent_id.sale_incoterm_id
        else:
            self.incoterm = self.partner_id.sale_incoterm_id
        return res

    @api.model
    def update_attention_to_note(self):
        sqlcheck = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='sale_order' and column_name='sale_attention_to_id'
        """
        self.env.cr.execute(sqlcheck)
        if self.env.cr.fetchone():
            sqlupdate = """
            update sale_order
            set sale_attention_to_note =
            (select name from res_partner where id = sale_attention_to_id)
            where sale_attention_to_id is not null and (sale_attention_to_note is null or
                                                        sale_attention_to_note = '')
            """
            self.env.cr.execute(sqlupdate)

    def write(self, vals):
        res = super().write(vals)
        for so in self:
            if "picking_note" in vals or "picking_customer_note" in vals:
                for picking in so.picking_ids.filtered(
                    lambda x: x.state not in ("done", "cancel")
                    and x.picking_type_code == "outgoing"
                ):
                    picking.write(
                        {
                            "note": vals.get("picking_note"),
                            "customer_note": vals.get("picking_customer_note"),
                        }
                    )
        return res
