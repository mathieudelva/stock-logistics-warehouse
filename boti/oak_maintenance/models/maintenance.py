from odoo import fields, models


# Inheriting maintenance.equipment and adding new fields
class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    sage_id = fields.Char(string="Sage Reference")
    sage_name = fields.Char()
