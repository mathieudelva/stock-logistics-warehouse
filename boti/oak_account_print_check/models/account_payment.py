# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.misc import format_date, formatLang

INV_LINES_PER_STUB = 8


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_stubbed_crop = fields.Boolean(compute="_compute_stubbed_crop", store=True)

    @api.depends("move_id", "company_id.account_check_printing_multi_stub")
    def _compute_stubbed_crop(self):
        for rec in self:
            multi_stub = rec.company_id.account_check_printing_multi_stub
            inv_lines = len(rec.move_id._get_reconciled_invoices())
            stubbed_crop = not multi_stub and inv_lines > INV_LINES_PER_STUB
            rec.is_stubbed_crop = stubbed_crop

    def _check_make_stub_pages(self):
        """The stub is the summary of paid invoices. It may spill on several pages,
        in which case only the check on first page is valid. This function returns
        a list of stub lines per page.
        """
        super()._check_make_stub_pages()

        self.ensure_one()

        def prepare_vals(invoice, partials):
            # START CUSTOMIZATION
            number = invoice.ref or invoice.name
            purchase_orders = ", ".join(
                invoice.mapped("invoice_line_ids.purchase_order_id.name")
            )
            discount_taken = invoice.discount_taken
            # END CUSTOMIZATION

            if invoice.is_outbound():
                invoice_sign = 1
                partial_field = "debit_amount_currency"
            else:
                invoice_sign = -1
                partial_field = "credit_amount_currency"

            if invoice.currency_id.is_zero(invoice.amount_residual):
                amount_residual_str = "-"
            else:
                amount_residual_str = formatLang(
                    self.env,
                    invoice_sign * invoice.amount_residual,
                    currency_obj=invoice.currency_id,
                )

            return {
                "due_date": format_date(self.env, invoice.invoice_date_due),
                "number": number,
                "amount_residual": amount_residual_str,
                "amount_total": formatLang(
                    self.env,
                    invoice_sign * invoice.amount_total,
                    currency_obj=invoice.currency_id,
                ),
                "currency": invoice.currency_id,
                # START CUSTOMIZATION
                "amount_paid": formatLang(
                    self.env,
                    invoice_sign * sum(partials.mapped(partial_field)) - discount_taken,
                    currency_obj=self.currency_id,
                ),
                "purchase_orders": purchase_orders,
                "discount_taken": formatLang(
                    self.env,
                    discount_taken,
                    currency_obj=invoice.currency_id,
                ),
                # END CUSTOMIZATION
            }

        # Decode the reconciliation to keep only invoices.
        term_lines = self.line_ids.filtered(
            lambda line: line.account_id.account_type
            in ("asset_receivable", "liability_payable")
        )
        invoices = (
            term_lines.matched_debit_ids.debit_move_id.move_id
            + term_lines.matched_credit_ids.credit_move_id.move_id
        ).filtered(lambda x: x.is_outbound())
        invoices = invoices.sorted(lambda x: x.invoice_date_due or x.date)

        # Group partials by invoices.
        invoice_map = {
            invoice: self.env["account.partial.reconcile"] for invoice in invoices
        }
        for partial in term_lines.matched_debit_ids:
            invoice = partial.debit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial
        for partial in term_lines.matched_credit_ids:
            invoice = partial.credit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial

        # Prepare stub_lines.
        if "out_refund" in invoices.mapped("move_type"):
            stub_lines = [{"header": True, "name": "Bills"}]
            stub_lines += [
                prepare_vals(invoice, partials)
                for invoice, partials in invoice_map.items()
                if invoice.move_type == "in_invoice"
            ]
            stub_lines += [{"header": True, "name": "Refunds"}]
            stub_lines += [
                prepare_vals(invoice, partials)
                for invoice, partials in invoice_map.items()
                if invoice.move_type == "out_refund"
            ]
        else:
            stub_lines = [
                prepare_vals(invoice, partials)
                for invoice, partials in invoice_map.items()
                if invoice.move_type == "in_invoice"
            ]

        # Crop the stub lines or split them on multiple pages
        if not self.company_id.account_check_printing_multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = (
                len(stub_lines) > INV_LINES_PER_STUB
                and INV_LINES_PER_STUB - 1
                or INV_LINES_PER_STUB
            )
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                if len(stub_lines) >= i + INV_LINES_PER_STUB and stub_lines[
                    i + INV_LINES_PER_STUB - 1
                ].get("header"):
                    num_stub_lines = INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
                else:
                    num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i : i + num_stub_lines])
                i += num_stub_lines

        return stub_pages

    def _check_make_stub_line(self, invoice):
        # START CUSTOMIZATION
        super()._check_make_stub_line(invoice)
        purchase_orders = ", ".join(
            invoice.mapped("invoice_line_ids.purchase_order_id.name")
        )
        # discount_taken = invoice.discount_taken
        # END CUSTOMIZATION
        # Return the dict used to display an invoice/refund in the stub
        # DEPRECATED: TO BE REMOVED IN MASTER
        # Find the account.partial.reconcile which are common to the
        # invoice and the payment
        if invoice.move_type in ["in_invoice", "out_refund"]:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.line_ids.mapped(
                "matched_debit_ids"
            ).filtered(lambda r: r.debit_move_id in self.line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.line_ids.mapped(
                "matched_credit_ids"
            ).filtered(lambda r: r.credit_move_id in self.line_ids)

        if self.currency_id != self.journal_id.company_id.currency_id:
            amount_paid = (
                abs(sum(invoice_payment_reconcile.mapped("amount_currency"))) - 0
            )
            # discount_taken
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped("amount"))) - 0
            # discount_taken

        amount_residual = invoice_sign * invoice.amount_residual

        return {
            "due_date": format_date(self.env, invoice.invoice_date_due),
            "number": invoice.ref or invoice.name,
            "amount_total": formatLang(
                self.env,
                invoice_sign * invoice.amount_total,
                currency_obj=invoice.currency_id,
            ),
            "amount_residual": formatLang(
                self.env, amount_residual, currency_obj=invoice.currency_id
            )
            if amount_residual * 10**4 != 0
            else "-",
            "amount_paid": formatLang(
                self.env, invoice_sign * amount_paid, currency_obj=self.currency_id
            ),
            "currency": invoice.currency_id,
            # START CUSTOMIZATION
            "purchase_orders": purchase_orders,
            "discount_taken": formatLang(
                self.env,
                0,
                currency_obj=invoice.currency_id,
            ),
            # discount_taken
            # END CUSTOMIZATION
        }
