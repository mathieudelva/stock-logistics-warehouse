from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    documents_helpdesk_settings = fields.Boolean(
        related="company_id.documents_helpdesk_settings",
        readonly=False,
        string="Helpdesk",
    )
    documents_helpdesk_folder = fields.Many2one(
        "documents.folder",
        related="company_id.documents_helpdesk_folder",
        readonly=False,
        string="helpdesk default workspace",
    )

    @api.onchange("documents_helpdesk_folder")
    def _onchange_documents_helpdesk_folder(self):
        # Implemented in other documents-helpdesk bridge modules
        pass
