# Copyright (c) OpenValue All Rights Reserved


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    mrp_parameter_ids = fields.One2many(
        "mrp.parameter", "product_id", "MRP Planning parameters"
    )
    mrp_parameter_count = fields.Integer(
        "MRP Planning Parameter Count",
        readonly=True,
        compute="_compute_mrp_parameter_count",
    )

    @api.depends("mrp_parameter_ids", "mrp_parameter_ids.active")
    def _compute_mrp_parameter_count(self):
        for product in self:
            if product.company_id:
                product.mrp_parameter_count = self.env["mrp.parameter"].search_count(
                    [
                        ("active", "=", True),
                        ("product_id", "=", product.id),
                        ("company_id", "=", product.company_id.id),
                    ]
                )
            else:
                product.mrp_parameter_count = self.env["mrp.parameter"].search_count(
                    [("active", "=", True), ("product_id", "=", product.id)]
                )

    def _compute_qty_available_locations(self, locations):
        qty_available = 0.0
        for product in self:
            no_availability_locations = self.env["stock.location"].search(
                [("no_availability", "=", True)]
            )
            locations -= no_availability_locations
            stock_quant_ids = self.env["stock.quant"].search(
                [("product_id", "=", product.id), ("location_id", "in", locations.ids)]
            )
            qty_available = sum(stock_quant_ids.mapped("quantity"))
        return qty_available

    def _compute_supply_method(self, warehouse_id):
        supply_method = "none"
        supply_method_man = supply_method_buy = False
        source_warehouse_id = False
        bom = False
        values = {"warehouse_id": warehouse_id, "company_id": warehouse_id.company_id}

        for product in self:
            # manufacture
            if warehouse_id.manufacture_steps == "pbm_sam":
                location = warehouse_id.sam_loc_id
            else:
                location = warehouse_id.lot_stock_id
            rule = self.env["procurement.group"]._get_rule(product, location, values)
            if rule and rule.action == "manufacture":
                supply_method_man = "manufacture"

            # buy/transfer
            if warehouse_id.reception_steps == "one_step":
                location = warehouse_id.lot_stock_id
            else:
                location = warehouse_id.wh_input_stock_loc_id
            rule = self.env["procurement.group"]._get_rule(product, location, values)
            if rule and rule.action == "buy":
                supply_method_buy = "buy"
                suppliers = product._prepare_sellers()
                if suppliers:
                    bom = self.env["mrp.bom"]._bom_subcontract_find(
                        product=product,
                        picking_type=None,
                        company_id=warehouse_id.company_id.id,
                        bom_type="subcontract",
                        subcontractor=suppliers[0].partner_id,
                    )
                if bom and bom.type == "subcontract":
                    supply_method_buy = "subcontracting"
            if rule and rule.action in ("pull", "push", "pull_push"):
                supply_method_buy = "transfer"
                source_warehouse_id = rule.propagate_warehouse_id

            if (
                supply_method == "none"
                and supply_method_buy == "transfer"
                and source_warehouse_id
            ):
                supply_method = "transfer"
            if supply_method == "none" and supply_method_man == "manufacture":
                supply_method = "manufacture"
            if supply_method == "none" and supply_method_buy == "buy":
                supply_method = "buy"
            if supply_method == "none" and supply_method_buy == "subcontracting":
                supply_method = "subcontracting"

        return supply_method
