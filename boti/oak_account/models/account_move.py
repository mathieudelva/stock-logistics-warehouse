# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_note = fields.Text()

    account_move_domain = fields.Char(
        compute="_compute_account_move_domain",
        readonly=True,
        store=False,
    )

    @api.depends("name")
    def _compute_account_move_domain(self):
        for rec in self:
            account_move_domain = "active"
            if rec.move_type in ("out_invoice", "out_refund", "out_receipt"):
                account_move_domain = "customer_rank"
            elif rec.move_type in ("in_invoice", "in_refund", "in_receipt"):
                account_move_domain = "supplier_rank"
            rec.account_move_domain = account_move_domain
