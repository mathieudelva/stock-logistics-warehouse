# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MoveLine(models.Model):
    _inherit = "account.move.line"

    product_category_id = fields.Many2one(related="product_id.categ_id", store=True)
    payment_state = fields.Selection(related="move_id.payment_state", store=True)
