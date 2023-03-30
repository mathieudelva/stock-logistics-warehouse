from odoo import fields, models


# visit assessments
class VisitAssessment(models.Model):
    _name = "visit.assessment"
    _description = "Visit Assessment"
    _check_company_auto = True

    name = fields.Char(
        name="Visit Assessment", required="True", help="Assessment of Visit"
    )
    description = fields.Text(name="Description")
