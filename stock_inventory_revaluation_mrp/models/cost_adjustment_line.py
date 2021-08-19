# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CostAdjustmentLine(models.Model):
    _inherit = "cost.adjustment.line"

    mrp_production_ids = fields.Many2many(
        "mrp.production",
        string="Manufacturing Orders",
        compute="_compute_set_productions_boms",
    )
    production_count = fields.Integer(
        string="MO's", compute="_compute_set_productions_boms", readonly=False
    )
    bom_ids = fields.Many2many(
        "mrp.bom", string="BOMs", compute="_compute_set_productions_boms"
    )
    bom_count = fields.Integer(
        string="BOM's", compute="_compute_set_productions_boms", readonly=False
    )

    @api.depends("product_id", "state")
    def _compute_set_productions_boms(self):
        for line in self:
            if line.state not in ("posted"):
                # Set MO's
                if line.mrp_production_ids:
                    line.mrp_production_ids = [(5,)]
                productions = self.env["mrp.production"].search(
                    [("state", "in", ["draft", "confirmed", "progress"])]
                )
                for production in productions:
                    components = production.move_raw_ids.mapped("product_id")
                    for product in components:
                        if line.product_id.id == product.id:
                            line.mrp_production_ids = [(4, production.id)]
                # Set BOMs
                if line.bom_ids:
                    line.bom_ids = [(5,)]
                bom_lines = self.env["mrp.bom.line"].search(
                    [("product_id", "=", line.product_id.id)]
                )
                for bom_line in bom_lines:
                    line.bom_ids = [(4, bom_line.bom_id.id)]
                line.production_count = len(line.mrp_production_ids)
                line.bom_count = len(line.bom_ids)

    def action_view_production(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_action")
        action["domain"] = [("id", "in", self.mapped("mrp_production_ids.id"))]
        action["context"] = dict(self._context, create=False)
        return action

    def action_view_bom(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.product_open_bom")
        action["domain"] = [("id", "in", self.mapped("bom_ids.id"))]
        action["context"] = dict(self._context, create=False)
        return action
