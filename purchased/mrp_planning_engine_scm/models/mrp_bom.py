from datetime import date

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    lt = fields.Float("LT (days)", compute="_compute_lead_times")
    dlt = fields.Float("DLT (days)", compute="_compute_lead_times")
    clt = fields.Float("CLT (days)", compute="_compute_lead_times")
    mrp_availability_check_warehouse_id = fields.Many2one(
        "stock.warehouse", "MRP Availability Check Warehouse"
    )

    def _get_decoupled_lead_time(self):
        if not self.bom_line_ids:
            return 0.0
        paths = [0] * len(self.bom_line_ids)
        i = 0
        for line in self.bom_line_ids:
            if line.is_stock:
                i += 1
            elif line.product_id.bom_ids:
                bom = line.product_id.bom_ids[0]
                if bom and bom.type == "normal":
                    paths[i] += (
                        bom.product_id.produce_delay
                        or bom.product_tmpl_id.produce_delay
                        or 0.0
                    )
                    paths[i] += bom._get_decoupled_lead_time()
                elif bom and bom.type == "subcontract":
                    subcontractors = bom.subcontractor_ids
                    subs = bom.product_id.seller_ids.filtered(
                        lambda sub: sub.partner_id in subcontractors
                    ) or bom.product_tmpl_id.seller_ids.filtered(
                        lambda sub: sub.partner_id in subcontractors
                    )
                    if subs:
                        paths[i] += subs[0].delay or 0.0
                    paths[i] += bom._get_decoupled_lead_time()
                i += 1
            else:
                if line.product_id.seller_ids:
                    paths[i] = line.product_id.seller_ids[0].delay
                i += 1
        return max(paths)

    def _get_comulative_lead_time(self):
        if not self.bom_line_ids:
            return 0.0
        paths = [0] * len(self.bom_line_ids)
        i = 0
        for line in self.bom_line_ids:
            if line.product_id.bom_ids:
                bom = line.product_id.bom_ids[0]
                if bom and bom.type == "normal":
                    paths[i] += (
                        bom.product_id.produce_delay
                        or bom.product_tmpl_id.produce_delay
                        or 0.0
                    )
                    paths[i] += bom._get_comulative_lead_time()
                elif bom and bom.type == "subcontract":
                    subcontractors = bom.subcontractor_ids
                    subs = bom.product_id.seller_ids.filtered(
                        lambda sub: sub.partner_id in subcontractors
                    ) or bom.product_tmpl_id.seller_ids.filtered(
                        lambda sub: sub.partner_id in subcontractors
                    )
                    if subs:
                        paths[i] += subs[0].delay or 0.0
                    paths[i] += bom._get_comulative_lead_time()
                i += 1
            else:
                if line.product_id.seller_ids:
                    paths[i] = line.product_id.seller_ids[0].delay
                i += 1
        return max(paths)

    @api.depends("product_id", "product_tmpl_id", "mrp_availability_check_warehouse_id")
    def _compute_lead_times(self):
        for record in self:
            dlt = lt = clt = 0.0
            if record.type == "normal":
                lt = (
                    record.product_id.produce_delay
                    or record.product_tmpl_id.produce_delay
                )
                dlt = lt + record._get_decoupled_lead_time()
                clt = lt + record._get_comulative_lead_time()
            elif record.type == "subcontract":
                subcontractors = record.subcontractor_ids
                subs = record.product_id.seller_ids.filtered(
                    lambda sub: sub.partner_id in subcontractors
                ) or record.product_tmpl_id.seller_ids.filtered(
                    lambda sub: sub.partner_id in subcontractors
                )
                if subs:
                    lt = subs[0].delay
                dlt = lt + record._get_decoupled_lead_time()
                clt = lt + record._get_comulative_lead_time()
            record.lt = lt
            record.dlt = dlt
            record.clt = clt


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    is_stock = fields.Boolean("Stock Buffered", compute="_compute_is_stock_buffered")
    lt = fields.Float("LT (days)", compute="_compute_lead_times")
    dlt = fields.Float("DLT (days)", compute="_compute_lead_times")
    clt = fields.Float("CLT (days)", compute="_compute_lead_times")
    mrp_availability_check_warehouse_id = fields.Many2one(
        "stock.warehouse", "MRP Availability Check Warehouse"
    )

    @api.depends("product_id", "mrp_availability_check_warehouse_id")
    def _compute_is_stock_buffered(self):
        for record in self:
            record.is_stock = False
            product = record.product_id
            reorder_point = self.env["mrp.parameter"].search(
                [
                    ("product_id", "=", product.id),
                    (
                        "warehouse_id",
                        "=",
                        record.mrp_availability_check_warehouse_id.id,
                    ),
                ],
                limit=1,
            )
            if reorder_point and reorder_point.mrp_type == "R":
                record.is_stock = True

    @api.depends("product_id", "mrp_availability_check_warehouse_id")
    def _compute_lead_times(self):
        for record in self:
            record.dlt = record.lt = record.clt = 0.0
            if record.product_id.bom_ids:
                record.dlt = record.product_id.bom_ids[0].dlt
                record.clt = record.product_id.bom_ids[0].clt
                record.lt = record.product_id.bom_ids[0].lt
            else:
                record.lt = record.dlt = record.clt = record._get_purchase_lt()

    def _get_purchase_lt(self):
        today = date.today()
        purchase_lt = 0.0
        for record in self:
            supplier = self.env["product.supplierinfo"].search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("date_start", "<=", today),
                    ("date_end", ">", today),
                ],
                limit=1,
            )
            if supplier:
                purchase_lt = supplier.delay
                continue
            supplier = self.env["product.supplierinfo"].search(
                [("product_id", "=", record.product_id.id)], limit=1
            )
            if supplier:
                purchase_lt = supplier.delay
                continue
            supplier = self.env["product.supplierinfo"].search(
                [
                    ("product_tmpl_id", "=", record.product_id.product_tmpl_id.id),
                    ("date_start", "<=", today),
                    ("date_end", ">", today),
                ],
                limit=1,
            )
            if supplier:
                purchase_lt = supplier.delay
                continue
            supplier = self.env["product.supplierinfo"].search(
                [("product_tmpl_id", "=", record.product_id.product_tmpl_id.id)],
                limit=1,
            )
            if supplier:
                purchase_lt = supplier.delay
        return purchase_lt
