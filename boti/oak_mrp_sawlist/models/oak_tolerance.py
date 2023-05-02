from odoo import fields, models


# Oak finish size tolerances
class OakTolerance(models.Model):
    _name = "oak.tolerance"
    _description = "Oak Finish Size Tolerances"
    _check_company_auto = True

    name = fields.Char(string="Tolerance", required="True")
    nformat = fields.Char(string="Number Format")
    description = fields.Text()
