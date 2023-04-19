from odoo import api, fields, models


# Material types
class HelpdeskCaseItems(models.Model):
    _name = "helpdesk.case.items"
    _description = "Helpdesk Incident Case Items"
    _check_company_auto = True

    case_item_id = fields.Many2one("helpdesk.ticket", "Helpdesk Ticket")

    quantity = fields.Float()

    ref_default_code = fields.Char("Code", help="Active or Legacy Product Code")

    ref_legacy = fields.Many2one(
        "product.legacy", "Legacy Item", help="Reference Legacy"
    )

    ref_product = fields.Many2one(
        "product.product", "Product", help="Reference Product"
    )

    description = fields.Text(string="Item Description")

    to_be_ordered = fields.Boolean()

    restocking_fee = fields.Boolean()

    to_be_returned = fields.Boolean()

    return_reason = fields.Many2one("helpdesk.return.reasons")

    date_returned = fields.Date()

    notes = fields.Text()

    @api.onchange("ref_product")
    def _onchange_ref_product(self):
        if self.ref_product:
            self.ref_default_code = self.ref_product.default_code
            self.description = self.ref_product.name
            self.ref_legacy = False

    @api.onchange("ref_legacy")
    def _onchange_ref_legacy(self):
        if self.ref_legacy:
            self.ref_default_code = self.ref_legacy.default_code
            self.description = self.ref_legacy.name
            self.ref_product = False
