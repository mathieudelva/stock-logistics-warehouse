import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    imported_from_shipstation = fields.Boolean(string="Imported From ShipStation")
    shipstation_customerId = fields.Char(string="Shipstation Customer ID")
