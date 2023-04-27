from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = "stock.package.type"

    package_carrier_type = fields.Selection(
        selection_add=[("shipstation", "Shipstation")],
        ondelete={"dhl_parcel": "set default"},
    )
