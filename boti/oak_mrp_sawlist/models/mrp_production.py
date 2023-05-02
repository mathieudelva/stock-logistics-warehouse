from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    _description = "Production Order"

    analytic_plan_id = fields.Many2one(
        related="analytic_account_id.plan_id", store=True
    )

    def load_components(self):
        # Clear move raws if we are changing the product.
        # In case of creation (self._origin is empty),
        # we need to avoid keeping incorrect lines,
        # so clearing is necessary too.
        if self.product_id != self._origin.product_id:
            self.move_raw_ids = [(5,)]
        if self.bom_id and self.product_qty > 0:
            # keep manual entries
            list_move_raw = [
                (4, move.id)
                for move in self.move_raw_ids.filtered(lambda m: not m.bom_line_id)
            ]
            moves_raw_values = self._get_moves_raw_values()
            move_raw_dict = {
                move.bom_line_id.id: move
                for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)
            }
            for move_raw_values in moves_raw_values:
                if move_raw_values["bom_line_id"] in move_raw_dict:
                    # update existing entries
                    list_move_raw += [
                        (
                            1,
                            move_raw_dict[move_raw_values["bom_line_id"]].id,
                            move_raw_values,
                        )
                    ]
                else:
                    # add new entries
                    list_move_raw += [(0, 0, move_raw_values)]
            self.move_raw_ids = list_move_raw
        else:
            self.move_raw_ids = [
                (2, move.id)
                for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)
            ]

    def create_workorders(self):
        for production in self:
            if not production.bom_id:
                continue
            workorders_values = []

            product_qty = production.product_uom_id._compute_quantity(
                production.product_qty, production.bom_id.product_uom_id
            )
            exploded_boms, dummy = production.bom_id.explode(
                production.product_id,
                product_qty / production.bom_id.product_qty,
                picking_type=production.bom_id.picking_type_id,
            )

            for bom, bom_data in exploded_boms:
                # If the operations of the parent BoM and phantom
                # BoM are the same, don't recreate work orders.
                if not (
                    bom.operation_ids
                    and (
                        not bom_data["parent_line"]
                        or bom_data["parent_line"].bom_id.operation_ids
                        != bom.operation_ids
                    )
                ):
                    continue
                for operation in bom.operation_ids:
                    workorders_values += [
                        {
                            "name": operation.name,
                            "production_id": production.id,
                            "workcenter_id": operation.workcenter_id.id,
                            "product_uom_id": production.product_uom_id.id,
                            "operation_id": operation.id,
                            "state": "pending",
                            "consumption": production.consumption,
                        }
                    ]
            production.workorder_ids = [(5, 0)] + [
                (0, 0, value) for value in workorders_values
            ]
            for workorder in production.workorder_ids:
                workorder.duration_expected = workorder._get_duration_expected()
