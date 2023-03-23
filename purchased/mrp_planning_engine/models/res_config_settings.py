from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # FIRMING_TYPE = [
    #    ("0", "Do Not Firm"),
    #    ("1", "Firm in Frozen Period and new proposals out of the Frozen Period"),
    #    ("2", "Firm in Frozen Period and no new proposals in the Frozen Period"),
    # ]

    forward_planning = fields.Boolean("Forward Planning")
    number_maximum_lots = fields.Integer(
        "Maximum number of lots", default=10, required=True
    )
    confirm_order = fields.Boolean("MO Confirmed")
    llc_recursion_limit = fields.Integer(
        "Recursion limit in LLC calculation", default=100, required=True
    )
    # roll_forward_period = fields.Integer('Roll Forward Period', default=0)
    # firming_type = fields.Selection(FIRMING_TYPE, 'Firming Type', default="0", required=True)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    forward_planning = fields.Boolean(
        related="company_id.forward_planning", readonly=False
    )
    number_maximum_lots = fields.Integer(
        related="company_id.number_maximum_lots", readonly=False
    )
    confirm_order = fields.Boolean(related="company_id.confirm_order", readonly=False)
    llc_recursion_limit = fields.Integer(
        related="company_id.llc_recursion_limit", readonly=False
    )
    # roll_forward_period = fields.Integer(related="company_id.roll_forward_period", readonly=False)
    # firming_type = fields.Selection(related="company_id.firming_type", readonly=False)
