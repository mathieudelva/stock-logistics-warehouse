from odoo import fields, models


# Inheriting the MrpBomLine Model and adding new fields
class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    # external ref to simplify pre golive BoM line syncronization
    external_ref = fields.Char("External Ref #")
