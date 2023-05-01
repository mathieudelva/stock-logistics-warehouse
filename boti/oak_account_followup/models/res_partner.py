# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Partner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "mail.activity.mixin", "mail.thread.blacklist"]
    _mail_flat_thread = False

    def _message_get_default_recipients(self):
        follower_ids = [i.partner_id.id for i in self.message_follower_ids]
        return {
            r.id: {
                "partner_ids": follower_ids or r.ids,
                "email_to": False,
                "email_cc": False,
            }
            for r in self
        }
