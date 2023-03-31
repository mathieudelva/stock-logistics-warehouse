from odoo import _, fields, models


class CreateEco(models.TransientModel):
    _name = "helpdesk.create.eco"
    _description = "Create a PLM ECO"

    helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Related ticket", required=True
    )
    company_id = fields.Many2one(related="helpdesk_ticket_id.company_id")
    name = fields.Char("Title", required=True)
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product",
        help="Product to use for the ECO",
        required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    eco_type_id = fields.Many2one(
        "mrp.eco.type", string="ECO Type", help="ECO Type", required=True
    )
    note = fields.Html(related="helpdesk_ticket_id.description")

    def action_generate_eco(self):
        self.ensure_one()
        return self.env["mrp.eco"].create(
            {
                "name": self.name,
                "helpdesk_ticket_id": self.helpdesk_ticket_id.id,
                "product_tmpl_id": self.product_tmpl_id.id,
                "type_id": self.eco_type_id.id,
                "note": self.note,
                "type": "product",
            }
        )

    def action_generate_and_view_eco(self):
        self.ensure_one()
        new_eco = self.action_generate_eco()
        return {
            "type": "ir.actions.act_window",
            "name": _("ECO from Tickets"),
            "res_model": "mrp.eco",
            "res_id": new_eco.id,
            "view_mode": "form",
            "view_id": self.env.ref("mrp_plm.mrp_eco_view_form").id,
        }
