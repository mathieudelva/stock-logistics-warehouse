# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ["stock.scrap", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["done"]

    _tier_validation_manual_config = False
