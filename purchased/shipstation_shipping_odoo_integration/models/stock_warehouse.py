import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    shipstation_warehouse_id = fields.Many2one(
        "shipstation.warehouse.detail", string="Shipstation Warehouse"
    )
