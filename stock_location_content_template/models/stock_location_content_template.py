# Copyright (c) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLocationContentTemplate(models.Model):
    _name = "stock.location.content.template"
    _description = "Stcok Location Content Template"

    name = fields.Char(string="Name")
    line_ids = fields.One2many(
        "stock.location.content.template.line", "template_id", string="Products"
    )
