from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    department_id = fields.Many2one(comodel_name="hr.department", required=True)
