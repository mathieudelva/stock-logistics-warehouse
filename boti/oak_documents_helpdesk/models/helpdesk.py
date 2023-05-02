from odoo import models


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _inherit = ["helpdesk.ticket", "documents.mixin"]

    def _get_document_folder(self):
        for ticket in self:
            if ticket.team_id:
                return self.env["documents.folder"]._create_helpdesk_folder(
                    ticket.team_id,
                    self.company_id,
                    self.company_id.documents_helpdesk_folder,
                )
            else:
                return self.company_id.documents_helpdesk_folder

    def _check_create_documents(self):
        return (
            self.company_id.documents_helpdesk_settings
            and super()._check_create_documents()
        )

    def _get_document_vals(self, attachment):
        if self._check_create_documents():
            # Get ticket info
            for ticket in self:
                # if we have a contact get id
                if ticket.partner_id:
                    partner_id = int(ticket.partner_id)
                # else leave blank
                else:
                    partner_id = None
            document_vals = {
                "attachment_id": attachment.id,
                "name": attachment.name or self.display_name,
                "folder_id": self._get_document_folder().id,
                "owner_id": self._get_document_owner().id,
                "tag_ids": [(6, 0, self._get_document_tags().ids)],
                "partner_id": partner_id,
            }
            return document_vals
