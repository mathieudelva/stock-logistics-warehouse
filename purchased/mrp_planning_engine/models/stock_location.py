from odoo import fields, models


class stock_location(models.Model):
    _inherit = "stock.location"

    no_availability = fields.Boolean("No stock availability in MRP Planning ")
