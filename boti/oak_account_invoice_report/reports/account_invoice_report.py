# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ReportInvoiceWithoutPayment(models.AbstractModel):
    _inherit = "report.account.report_invoice"

    @api.model
    def _get_report_values(self, docids, data=None):
        rslt = super()._get_report_values(docids, data)
        custom_doc = []
        for rec in rslt.get("docs"):
            my_dict = self._get_sale_picking_ref(rec)
            custom_doc.append(my_dict)
            rslt["cust_docs"] = custom_doc
        return rslt

    def _get_sale_picking_ref(self, result):
        track_no = []
        ship_date = []
        sale_id = result.invoice_line_ids.mapped("sale_line_ids").mapped("order_id")
        picking_ids = sale_id.picking_ids.search(
            [
                ("state", "=", "done"),
                ("sale_id", "=", sale_id.id),
            ]
        )
        if not len(picking_ids) > 1:
            track_no.append(picking_ids.carrier_tracking_ref)
            ship_date.append(picking_ids.date_done)
        else:
            for pick in picking_ids:
                track_no.append(pick.carrier_tracking_ref)
                ship_date.append(pick.date_done)
        my_dict = {
            "sale_id": sale_id,
            "track_no": track_no,
            "ship_date": ship_date,
            "inv_id": result.id,
        }
        return my_dict
