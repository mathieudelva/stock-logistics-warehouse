from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _domain_company(self):
        company = self.env.company
        return ["|", ("company_id", "=", False), ("company_id", "=", company.id)]

    documents_helpdesk_settings = fields.Boolean()
    documents_helpdesk_folder = fields.Many2one(
        "documents.folder",
        string="Helpdesk",
        domain=_domain_company,
        default=lambda self: self.env.ref(
            "oak_documents_helpdesk.documents_helpdesk_folder", raise_if_not_found=False
        ),
    )
