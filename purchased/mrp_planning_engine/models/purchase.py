from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        for order in self:
            for line in order.order_line:
                component_mrp_element = self.env["mrp.element"].search(
                    [
                        ("purchase_line_id", "=", line.id),
                        ("mrp_origin", "=", "spo"),
                        ("mrp_type", "=", "d"),
                    ]
                )
                if component_mrp_element:
                    component_mrp_element.unlink()
        return super().button_confirm()

    def button_cancel(self):
        for line in self.order_line:
            component_mrp_element = self.env["mrp.element"].search(
                [
                    ("purchase_line_id", "=", line.id),
                    ("mrp_origin", "=", "spo"),
                    ("mrp_type", "=", "d"),
                ]
            )
            if component_mrp_element:
                component_mrp_element.unlink()
        return super().button_cancel()

    def button_draft(self):
        for line in self.order_line:
            mrp_parameter = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", line.product_id.id),
                    (
                        "warehouse_id",
                        "=",
                        line.order_id.picking_type_id.warehouse_id.id,
                    ),
                ],
                limit=1,
            )
            # generazione dei fabbisogni di subcontracting dei componenti per le RfQs di subcontracting
            if mrp_parameter and mrp_parameter.supply_method == "subcontracting":
                bom = self.env["mrp.bom"]._bom_subcontract_find(
                    product=mrp_parameter.product_id,
                    picking_type=None,
                    company_id=mrp_parameter.warehouse_id.company_id.id,
                    bom_type="subcontract",
                    subcontractor=mrp_parameter.main_supplier_id,
                )
                for bomline in bom.bom_line_ids:
                    bomline_mrp_parameter_id = self.env["mrp.parameter"].search(
                        [
                            ("product_id", "=", bomline.product_id.id),
                            ("warehouse_id", "=", mrp_parameter.warehouse_id.id),
                        ],
                        limit=1,
                    )
                    if bomline_mrp_parameter_id and not bomline.product_qty <= 0.00:
                        sub_rfq_element_data = bomline_mrp_parameter_id._prepare_mrp_element_data_from_sub_rfq(
                            line, bomline
                        )
                        self.env["mrp.element"].create(sub_rfq_element_data)
        return super().button_draft()
