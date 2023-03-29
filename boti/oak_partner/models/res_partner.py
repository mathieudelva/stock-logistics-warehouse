from odoo import api, fields, models


# Inheriting the res.partner and adding new fields
class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    name = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)

    # new fields
    street3 = fields.Char(tracking=True)
    street4 = fields.Char(tracking=True)

    city = fields.Char(tracking=True)
    state_id = fields.Many2one(tracking=True)
    zip = fields.Char(tracking=True)
    country_id = fields.Many2one(tracking=True)
    legal_id_number = fields.Char(tracking=True)
    property_supplier_payment_term_id = fields.Many2one(tracking=True)
    property_payment_method_id = fields.Many2one(tracking=True)
    property_account_receivable_id = fields.Many2one(tracking=True)
    property_account_payable_id = fields.Many2one(tracking=True)

    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        company_dependent=True,
        help="The internal user in charge of this contact.",
    )

    extrep_id = fields.Many2one(
        "res.partner",
        string="External Sales Rep",
        help="External Sales Representative Partner",
    )

    parent_ref = fields.Char(
        string="Parent Account", store=True, related="parent_id.ref"
    )

    is_sales_rep = fields.Boolean(string="Is External Sales Rep")

    def filter_out_internal_users(self):
        internal_user = self.env.ref("base.group_user")
        return self.filtered(
            lambda x: x.email and internal_user not in x.user_ids.groups_id
        )

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        self.ref = self.parent_ref

    @api.onchange("type")
    def _onchange_type(self):
        if self.type in ["contact", "other", "private"]:
            self.ref = ""
        else:
            if not self.ref:
                for record in self:
                    self.ref = record.parent_ref
