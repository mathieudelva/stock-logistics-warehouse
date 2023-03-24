from odoo import fields, models


# Sale lead time messages
class SaleLeadtimeMessage(models.Model):
    _name = "sale.leadtime.message"
    _description = "Quotation Lead Time Messages"

    name = fields.Char(required="True")

    description = fields.Text(required="True")
