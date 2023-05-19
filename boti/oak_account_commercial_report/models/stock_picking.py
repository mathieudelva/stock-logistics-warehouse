# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ship_city = fields.Char("Shipment City")

    def get_move_details(self):
        rslt = {}
        custom_doc = []
        for _rec in self:
            my_dict = self.get_move_values()
            custom_doc.append(my_dict)
            rslt["cust_docs"] = custom_doc

        return rslt

    def get_move_values(self):
        move_dict = {}
        name = ""
        invoice_date = ""
        invoice_payment_term_id = ""
        invoice_incoterm_id = ""
        narration = ""
        for move in self.sale_id.invoice_ids:
            if move.name:
                name += move.name + ","
            if move.invoice_date:
                invoice_date += str(move.invoice_date) + ","
            if move.invoice_payment_term_id:
                invoice_payment_term_id += move.invoice_payment_term_id.name + ","
            if move.invoice_incoterm_id:
                invoice_incoterm_id += move.invoice_incoterm_id.name + ","
            if move.narration:
                narration += move.narration + ","
        move_dict.update(
            {
                "name": name,
                "invoice_date": invoice_date,
                "invoice_payment_term_id": invoice_payment_term_id,
                "invoice_incoterm_id": invoice_incoterm_id,
                "narration": narration,
            }
        )
        return move_dict

    def get_do_lines(self):
        pick_lines = []
        bom_parent_id = []
        for move in self.move_ids_without_package:
            line = {}
            country = move.sale_line_id.product_id.intrastat_origin_country_id.name
            default_code = move.sale_line_id.product_id.default_code
            if move.product_id.bom_line_ids.mapped("bom_id"):
                if move.sale_line_id.product_id not in bom_parent_id:
                    bom_parent_id.append(move.sale_line_id.product_id)
                    for _parent in bom_parent_id:
                        line.update(
                            {
                                "product_id": move.sale_line_id.product_id,
                                "default_code": default_code,
                                "country_of_origin": country,
                                "description": move.sale_line_id.name,
                                "product_qty": move.sale_line_id.product_uom_qty,
                                "price": move.sale_line_id.price_unit,
                                "amount": move.sale_line_id.price_unit,
                            }
                        )
            else:
                line.update(
                    {
                        "product_id": move.product_id,
                        "country_of_origin": country,
                        "default_code": default_code,
                        "description": move.description_picking,
                    }
                )
                qty = 0.0
                if move.state != "done":
                    line.update({"product_qty": move.product_uom_qty})
                    qty = move.product_uom_qty

                elif move.state == "done":
                    line.update({"product_qty": move.quantity_done})
                    qty = move.quantity_done
                price = move.picking_id.sale_id.order_line.filtered(
                    lambda product: product.product_id == move.product_id
                ).price_unit
                amount = qty * price
                line.update({"price": price, "amount": amount})
            pick_lines.append(line)
            line = False
        return pick_lines
