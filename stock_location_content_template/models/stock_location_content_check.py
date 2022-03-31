# Copyright (C) 2021 Casai (https://www.casai.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StocklocationContentCheck(models.Model):
    _name = "stock.location.content.check"
    _description = "Stock Location Content Check"

    name = fields.Char(string="Name", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
    )
    date = fields.Datetime(string="Date", required=True)
    location_id = fields.Many2one("stock.location", string="Location", required=True)
    user_id = fields.Many2one(
        "res.users", string="User", required=True, default=lambda self: self.env.user
    )
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company.id
    )
    line_ids = fields.One2many(
        "stock.location.content.check.line", "check_id", string="Products"
    )

    @api.depends("location_id")
    def _onchange_location_id(self):
        for rec in self:
            if rec.location_id.template_id:
                rec.line_ids = [(6, 0, [])]

    def action_confirm(self):
        for rec in self:
            rec.state = "confirmed"

    def action_complete(self):
        for rec in self:
            rec.state = "closed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
