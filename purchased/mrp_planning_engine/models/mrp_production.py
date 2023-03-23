from odoo import _, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mto_origin = fields.Char("MTO Origin", readonly=True)

    def _action_explode_bom(self):
        for production in self:
            if not production.move_raw_ids:
                moves_raw_values = production._get_moves_raw_values()
                list_move_raw = []
                for move_raw_values in moves_raw_values:
                    list_move_raw += [(0, _, move_raw_values)]
                production.move_raw_ids = list_move_raw
                production.move_raw_ids.write(
                    {
                        "group_id": production.procurement_group_id.id,
                        "reference": production.name,
                    }
                )
            if not production.move_finished_ids:
                move_finished_values = production._get_moves_finished_values()
                list_move_finished = []
                for move_finished_value in move_finished_values:
                    list_move_finished += [(0, _, move_finished_value)]
                production.move_finished_ids = list_move_finished
                production.move_finished_ids.write(
                    {
                        "group_id": production.procurement_group_id.id,
                        "reference": production.name,
                    }
                )
            if not production.workorder_ids:
                production._compute_workorder_ids()
