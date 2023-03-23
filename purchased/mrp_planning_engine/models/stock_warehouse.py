from odoo import _, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    planning_run = fields.Boolean()

    def _get_engine_locations(self):
        location_ids = False
        for warehouse in self:
            stock_locations_domain = [
                ("usage", "=", "internal"),
                ("company_id", "=", warehouse.company_id.id),
                "|",
                ("id", "child_of", warehouse.view_location_id.id),
                ("id", "child_of", warehouse.company_id.subcontracting_location_id.id),
            ]
            location_ids = self.env["stock.location"].search(stock_locations_domain)
        return location_ids

    # planning run in background mode a livello di warehouse
    def action_planning_engine_run(self):
        t_mess_id = False
        self.planning_run = True
        message = self.env["mrp.planning.engine.run"].planning_engine_run(self)
        self.planning_run = False
        if message:
            t_mess_id = (
                self.env["mrp.planning.message"]
                .create({"name": "planning run performed"})
                .id
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("MRP Planning Run Results"),
            "res_model": "mrp.planning.message",
            "res_id": t_mess_id,
            "views": [
                (
                    self.env.ref(
                        "mrp_planning_engine.view_mrp_planning_message_form"
                    ).id,
                    "form",
                )
            ],
            "target": "new",
        }
