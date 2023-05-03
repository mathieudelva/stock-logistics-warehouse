from odoo import models


class DocumentsFolder(models.Model):
    _name = "documents.folder"
    _inherit = ["documents.folder"]

    def _create_helpdesk_folder(self, team_id, company_id, parent_id):
        # search for team with team id
        team = self.env["helpdesk.team"].browse(int(team_id))
        if team:
            # find folder using team name
            folder = self.env["documents.folder"].search(
                [
                    ("name", "=", team.name),
                    ("parent_folder_id", "=", int(parent_id)),
                    ("company_id", "=", int(company_id)),
                ],
                limit=1,
            )
            folder_id = parent_id
            # check for folder & return id
            if folder:
                folder_id = folder
            # else create folder
            else:
                # get last available sequence
                folder_ids = self.env["documents.folder"].search(
                    [], limit=1, order="sequence desc"
                )
                for last_folder_id in folder_ids:
                    last_folder = self.env["documents.folder"].browse(
                        int(last_folder_id)
                    )
                    # create new folder with last available sequence
                    folder_id = super().create(
                        [
                            {
                                "company_id": int(company_id),
                                "parent_folder_id": int(parent_id),
                                "name": team.name,
                                "sequence": int(last_folder.sequence) + 1,
                            }
                        ]
                    )
        return folder_id
