from odoo import fields, models


class ShipstationProductData(models.Model):
    _name = "shipstation.product.data"
    _description = "Shipstation Product Data"

    store_id = fields.Many2one("shipstation.store.vts", string="Store")
    product_sku = fields.Char(string="Shipstation Product SKU")
    product_name = fields.Char(string="Shipstation Product Name")
    product_qty = fields.Char(string="Shipstation Product Qty")
