import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


# Inheriting the Product Model and adding new fields
class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template"
    _order = "name"

    # Needed fot the the product.combine database view
    finish_size = fields.Char(string="Finished size")

    bom_count_legacy = fields.Integer(
        "Legacy BoMs", compute="_compute_bom_count_legacy", compute_sudo=False
    )

    routing_count = fields.Integer(
        "Legacy Routings", compute="_compute_routing_count_legacy", compute_sudo=False
    )

    def _compute_routing_count_legacy(self):
        for record in self:
            try:
                record.routing_count = self.env["mrp.routing.legacy"].search_count(
                    [("itemid", "=", record.default_code)]
                )
            except ValueError:
                record.routing_count = 0

    def _compute_bom_count_legacy(self):
        for record in self:
            try:
                record.bom_count_legacy = self.env["mrp.bom.legacy"].search_count(
                    [("name", "=", record.default_code)]
                )
            except ValueError:
                record.bom_count = 0

    def get_legacy_bom_count(self):
        for record in self:
            return self.env["mrp.bom.legacy"].search_count(
                [("name", "=", record.default_code)]
            )
