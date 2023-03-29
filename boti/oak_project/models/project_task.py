from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    partner_id = fields.Many2one(tracking=True)
    parent_id = fields.Many2one(tracking=True)
    planned_date_begin = fields.Datetime(tracking=True)
    planned_date_end = fields.Datetime(tracking=True)
