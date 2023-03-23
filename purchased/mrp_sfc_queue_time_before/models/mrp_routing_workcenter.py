from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    queue_time_before = fields.Float("Queue Time Before")
