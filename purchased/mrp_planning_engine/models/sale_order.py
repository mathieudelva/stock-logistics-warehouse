from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    reduced_qty = fields.Float(
        "Demand Reduction Qty",
        digits="Product Unit of Measure",
        readonly=True,
        default=0.0,
        copy=False,
    )
    commitment_date = fields.Datetime("Delivery Date")

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id)
        if self.commitment_date:
            vals.update(
                {
                    "date_planned": self.commitment_date
                    - relativedelta(days=self.order_id.company_id.security_lead),
                    "date_deadline": self.commitment_date,
                }
            )
        return vals

    def write(self, values):
        commitment_date = values.get("commitment_date")
        if commitment_date:
            self.move_ids.date = fields.Datetime.to_datetime(
                commitment_date
            ) - relativedelta(days=self.company_id.security_lead)
            self.move_ids.date_deadline = commitment_date
        return super().write(values)

    @api.constrains("product_uom_qty", "commitment_date")
    def _check_demand_reduction(self):
        for line in self:
            mrp_parameter = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", line.product_id.id),
                    ("warehouse_id", "=", line.order_id.warehouse_id.id),
                ],
                limit=1,
            )
            if (
                mrp_parameter
                and mrp_parameter.demand_indicator in ("40", "50")
                and line.order_id.state in ("sale", "done")
            ):
                raise UserError(
                    _(
                        "it is not possible to change quantity item because reduction process already in progress."
                    )
                )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        for picking in self.picking_ids:
            for move in picking.move_ids.filtered(
                lambda r: r.state not in ("cancel", "done")
            ):
                for line in self.order_line:
                    move.write(
                        {
                            "date": (line.commitment_date or fields.Datetime.now())
                            - relativedelta(days=self.company_id.security_lead)
                        }
                    )
                mrp_parameter = self.env["mrp.parameter"].search(
                    [
                        ("product_id", "=", move.product_id.id),
                        ("warehouse_id", "=", move.warehouse_id.id),
                    ],
                    limit=1,
                )
                # strategies 40 and 50
                if (
                    mrp_parameter
                    and move.sale_line_id
                    and mrp_parameter.demand_indicator in ("40", "50")
                ):
                    backward_days = mrp_parameter.mrp_demand_backward_day or 1
                    delivery_date = (
                        move.sale_line_id.commitment_date
                        or move.sale_line_id.order_id.commitment_date
                        or move.sale_line_id.order_id.expected_date
                        or move.sale_line_id.order_id.date_order
                    )
                    backward_date = delivery_date - timedelta(days=backward_days)
                    customer_location_id = (
                        move.sale_line_id.order_id.partner_id.with_company(
                            move.company_id
                        ).property_stock_customer
                    )
                    if move.location_dest_id == customer_location_id:
                        backward_demand_items = self.env["mrp.demand"].search(
                            [
                                ("mrp_parameter_id", "=", mrp_parameter.id),
                                ("state", "=", "done"),
                                ("date_planned", "<=", delivery_date),
                                ("date_planned", ">", backward_date),
                            ]
                        )
                        qty = move.product_uom_qty
                        move._reduce_demand(qty, backward_demand_items)
        return res

    def action_cancel(self):
        for picking in self.picking_ids.filtered(
            lambda r: r.state not in ("cancel", "done")
        ):
            for move in picking.move_ids:
                mrp_parameter = self.env["mrp.parameter"].search(
                    [
                        ("product_id", "=", move.product_id.id),
                        ("warehouse_id", "=", move.warehouse_id.id),
                    ],
                    limit=1,
                )
                # strategies 40 and 50
                if (
                    mrp_parameter
                    and move.sale_line_id
                    and mrp_parameter.demand_indicator in ("40", "50")
                ):
                    backward_days = mrp_parameter.mrp_demand_backward_day or 1
                    delivery_date = (
                        move.sale_line_id.commitment_date
                        or move.sale_line_id.order_id.commitment_date
                        or move.sale_line_id.order_id.expected_date
                        or move.sale_line_id.order_id.date_order
                    )
                    backward_date = delivery_date - timedelta(days=backward_days)
                    customer_location_id = (
                        move.sale_line_id.order_id.partner_id.with_company(
                            move.company_id
                        ).property_stock_customer
                    )
                    if move.location_dest_id == customer_location_id:
                        backward_demand_items = (
                            self.env["mrp.demand"]
                            .search(
                                [
                                    ("mrp_parameter_id", "=", mrp_parameter.id),
                                    ("state", "=", "done"),
                                    ("date_planned", "<=", delivery_date),
                                    ("date_planned", ">", backward_date),
                                ]
                            )
                            .sorted(key=lambda r: r.date_requested)
                        )
                        qty = move.product_uom_qty
                        move._restore_demand(qty, backward_demand_items)
        return super().action_cancel()

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        res = super()._onchange_commitment_date()
        for line in self.order_line:
            if not line.commitment_date:
                line.commitment_date = self.commitment_date
        return res
