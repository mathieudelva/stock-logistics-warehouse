# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MRPWorkOrder(models.Model):
    _inherit = "mrp.workorder"

    # create wip adjustment journal entry
    def _wip_validate_entries(self, driver, quantity, description, cost):

        self.ensure_one()
        am_vals = []
        if self.restrict_partner_id and self.restrict_partner_id != self.company_id.partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return am_vals

        accounts = self._get_accounts_for_wip(driver)

        if cost < 0:
            debit_acc = accounts['expense'].id
            credit_acc = accounts['stock_wip'].id
        else:
            credit_acc = accounts['expense'].id
            debit_acc = accounts['stock_wip'].id

        aml_vals = self._prepare_wip_account_move_line(quantity, abs(cost), credit_acc, debit_acc, description)
        am_vals = {
            'journal_id': accounts['stock_journal'].id,
            'line_ids': aml_vals,
            'date': fields.Date.context_today(self),
            'ref': description,
            'move_type': 'entry',
        }

        account_moves = self.env['account.move'].sudo().create(am_vals)
        account_moves._post()


    # write JE for the stock_moves
    def _account_move_wip_entries(self, delta):

        # for each workorder
        for wo in self:
            wo_product = wo.workcenter_id.product_id
            drivers = wo_product.activity_cost_ids.mapped(product_id)
            for driver in drivers:
                if not driver.id in delta.keys():
                    continue
                cost_diff = delta[driver.id]
                amount_diff = cost_diff * abs(wo.duration)
                if amount_diff != 0:
                    description = "{} {}-{}".format("WIP Revaluation", wo.workcenter_id.name,move.driver.name)
                    wo._wip_validate_entries(driver, wo.duration, description, amount_diff)
            else:
                continue
        return True

    def _generate_wip_valuation_lines_data(self, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'balance': debit_value,
            'account_id': debit_account_id,
        }

        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'balance': -credit_value,
            'account_id': credit_account_id,
        }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        return rslt

    def _prepare_wip_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        self.ensure_one()

        debit_value = self.company_id.currency_id.round(cost)
        credit_value = debit_value

        res = [(0, 0, line_vals) for line_vals in self._generate_wip_valuation_lines_data(qty, debit_value, credit_value, debit_account_id, credit_account_id, description).values()]
        return res

    def _get_accounts_for_wip(self, product):

        if product:
            categ = self.product_id.categ_id
            accounts = product.product_tmpl_id.get_product_accounts()
        else:
            # If no product, get account from a configured default category
            get_param = self.env["ir.config_parameter"].sudo().get_param
            categ_xmlid = get_param("wip_default_product_category")
            categ = self.env.ref(categ_xmlid)
            accounts = {
                "stock_input": categ.property_stock_account_input_categ_id,
                "stock_output": categ.property_stock_account_output_categ_id,
                "stock_valuation": categ.property_stock_valuation_account_id,
                "stock_journal": categ.property_stock_journal,
            }
        if not accounts.get("stock_journal"):
            exceptions.ValidationError(
                _(
                    "Missing Stock Journal for Category %(categ_name)s when closing %(name)s",
                    categ_name=categ.display_name,
                    name=self.display_name,
                )
            )
        accounts.update(
            {
                "stock_wip": categ.property_wip_account_id,
                "stock_variance": categ.property_variance_account_id,
            }
        )

        return accounts

