from odoo import fields, models


class ShipstationWarehouseDetail(models.Model):
    _name = "shipstation.warehouse.detail"
    _description = "Shipstation Warehouse Detail"
    _order = "id desc"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Warehouse name")
    warehouse_id = fields.Char(string="Warehuse Id")
