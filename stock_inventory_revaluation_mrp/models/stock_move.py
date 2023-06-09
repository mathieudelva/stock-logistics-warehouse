# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"


    def _get_accounts_for_wip(self):

        if self.product_id:
            categ = self.product_id.categ_id
            accounts = self.product_id.product_tmpl_id.get_product_accounts()
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

        dest_location = self.stock_move_id.location_dest_id or (
            self.product_id.type == "product"
            and self.product_id.property_stock_production
        )
        # Only set for raw materials
        if dest_location and dest_location.valuation_in_account_id:
            accounts["stock_input"] = dest_location.valuation_in_account_id
            accounts["stock_wip"] = accounts["stock_input"]
            accounts["stock_variance"] = dest_location.valuation_variance_account_id
        if dest_location and dest_location.valuation_out_account_id:
            accounts["stock_output"] = dest_location.valuation_out_account_id
        return accounts

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

    # create wip adjustment journal entry
    def _wip_validate_entries(self, quantity, description, cost):

        self.ensure_one()
        am_vals = []
        if self.restrict_partner_id and self.restrict_partner_id != self.company_id.partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return am_vals

        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

        accounts = self._get_account_for_wip()

        if cost < 0:
            debit_acc = accounts['expense']
            credit_acc = accounts['stock_wip']
        else:
            credit_acc = stock_revaluation_account
            debit_acc = accounts['stock_wip']

        acc_src = accounts['expense']
        acc_dest = stock_production account
        
        am_vals.append(self.with_company(company_from)._prepare_wip_account_move_line(quantity, cost, credit_acc, debit_acc, accounts['stock_journal'], description))

        account_moves = self.env['account.move'].sudo().create(am_vals)
        account_moves._post()
       

    # write JE for the stock_moves
    def _account_move_wip_entries(self):

        # for each move
        for move in self:
            if move.product_type == 'stock' and move.with_company(svl.company_id).product_id.valuation == 'real_time':
                svls = self.env['stock.valuation.layer'].search([('stock_move_id','=',move.id)])
                for svl  in svls:
                    cost_diff = move.product_id.standard_price - svl.unit_cost
                    amount_diff = cost_diff * svl.quantity
                    if amount_diff != 0:
                        move._wip_validate_entries(svl.quantity, "Revaluation", amount_diff)
            else:
                continue
        return True

