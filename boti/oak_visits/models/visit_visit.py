from odoo import fields, models


class Visit(models.Model):
    _inherit = ["visit.visit"]

    READONLYSTATES = {"done": [("readonly", True)], "cancel": [("readonly", True)]}

    ref_product_id = fields.Many2one(
        "product.product",
        string="Reference Product",
        states=READONLYSTATES,
        ondelete="set null",
    )

    assessment_id = fields.Many2one(
        "visit.assessment", string="Current Assessment", ondelete="set null"
    )
    product_status_id = fields.Many2one(
        "visit.product.status", string="Using Our Equipment", ondelete="set null"
    )
    visit_reason_id = fields.Many2one(
        "visit.reason", string="Purpose", ondelete="set null"
    )
    competitor_equipment = fields.Text("Competitor Machines")
    external_ref = fields.Char("External DB Reference", help="For migration only!")
