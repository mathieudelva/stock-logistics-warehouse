from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def oak_helpdesk_create(self, values):

        # Write as Odoobot if creator_id is not set
        if not values.get("creator_id"):
            self.env.uid = 1
        else:
            self.env.uid = values.get("creator_id")

        del values["creator_id"]

        # Get our current helpdesk teams - let them send in the name
        if not values.get("team_name"):
            return "team_name is required"

        team = self.env["helpdesk.team"].search(
            [
                ("name", "=", values.get("team_name")),
            ],
            limit=1,
        )

        if not team:
            return "team_name not found"

        values["team_id"] = team.id
        del values["team_name"]

        # lookup a partner_id for a user_id to set as customer
        if values.get("requestor_id"):
            partner = self.env["res.users"].search(
                [
                    ("id", "=", values.get("requestor_id")),
                ],
            )

            if partner:
                values["partner_id"] = partner.partner_id.id

        del values["requestor_id"]

        # lookup a tag for tag_ids
        if values.get("tag_name"):
            tag = self.env["helpdesk.tag"].search(
                [
                    ("name", "=", values.get("tag_name")),
                ],
            )

            if tag:
                values["tag_ids"] = [tag.id]

        del values["tag_name"]

        # continue with the create as usual and return our ID
        rec = super(HelpdeskTicket, self).create(values)

        return rec.id
