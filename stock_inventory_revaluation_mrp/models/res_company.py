# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    lock_cost_products = fields.Boolean(string="Lock Costs on Products", copy=False)
    no_of_bom_version = fields.Integer(
        "Number of retained cost roll versions", default=1
    )

    @api.constrains("no_of_bom_version")
    def check_no_of_bom_version(self):
        if self.no_of_bom_version < 1:
            raise UserError(
                _("Number of retained cost roll versions needs to be a positive value.")
            )
