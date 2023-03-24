# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

TICKET_PRIORITY = [
    ("0", "All"),
    ("1", "Low priority"),
    ("2", "High priority"),
    ("3", "Urgent"),
]  # ent_13


class TicketMergeWizard(models.TransientModel):
    _name = "ticket.merge.wizard"
    _description = "Helpdesk Ticket Merge Wizard"

    merge_ticket_line_ids = fields.One2many(
        "merge.ticket.line",
        "primary_ticket_merge_id",
        string="Merge Ticket Line",
        readonly=True,
    )
    # merge_new_ticket_line_ids = fields.One2many(
    #     'merge.ticket.line',
    #     'ticket_merge_id',
    #     string="Merge Ticket Line",
    # ) #ent_13
    # support_ticket_ids = fields.Many2many(
    #    'helpdesk.ticket',
    #    string="Merge Tickets",
    # )
    support_ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Set as Primary Ticket",
    )
    responsible_user_id = fields.Many2one(
        "res.users",
        string="Responsible User",
        required=True,
    )
    team_id = fields.Many2one(
        "helpdesk.team",
        string="Support Team",
        required=True,
    )
    create_new_ticket = fields.Boolean(string="Create New Ticket?")
    ticket_subject = fields.Char(string="Subject")
    primary_id = fields.Many2one(
        "helpdesk.ticket",
        string="Primary Ticket",
    )
    merge_ids = fields.Many2many(
        "helpdesk.ticket",
        string="Merge Ticket",
    )
    is_sure = fields.Boolean(
        string="Are You Sure ?",
    )
    merge_reason = fields.Char(
        string="Merge Reason",
        required=True,
    )
    partner_id = fields.Many2one("res.partner", string="Customer")  # ent_13
    partner_name = fields.Char(string="Customer Name")  # ent_13
    partner_email = fields.Char(string="Customer Email")  # ent_13
    ticket_type_id = fields.Many2one(
        "helpdesk.ticket.type", string="Ticket Type"
    )  # ent_13
    priority = fields.Selection(
        TICKET_PRIORITY, string="Priority", default="0"
    )  # ent_13
    tag_ids = fields.Many2many("helpdesk.tag", string="Tags")  # ent_13

    @api.model
    def default_get(self, fields):
        res = super(TicketMergeWizard, self).default_get(fields)
        tecket_obj = self.env["helpdesk.ticket"]
        ticket_ids = tecket_obj.search([("id", "in", self._context.get("active_ids"))])
        ticket_line = self.env["merge.ticket.line"]
        # if all([x.partner_id == ticket_ids[0].partner_id
        #         for x in ticket_ids]) or\
        #    all([x.email == ticket_ids[0].email for x in ticket_ids]) or\
        #    all([x.phone == ticket_ids[0].phone for x in ticket_ids]):
        # if all([x.partner_id == ticket_ids[0].partner_id
        #         for x in ticket_ids]) or\
        #    all([x.partner_id.commercial_partner_id == ticket_ids[0].partner_id.commercial_partner_id for x in ticket_ids]) or\
        #    all([x.partner_id.child_ids == ticket_ids[0].partner_id.child_ids for x in ticket_ids]): #ent_13
        if all(
            [
                x.partner_id.commercial_partner_id
                in ticket_ids[0].partner_id.commercial_partner_id
                for x in ticket_ids
            ]
        ):  # ent_13
            if "merge_ticket_line_ids" in fields:

                tags = []
                for ticket in ticket_ids:
                    vals = {
                        "ticket_id": ticket.id,
                        # 'subject': ticket.subject,
                        "subject": ticket.name,  # ent_13
                    }
                    ticket_line += ticket_line.create(vals)
                    if ticket.tag_ids:
                        tags.extend(ticket.tag_ids.ids)
                        tags = list(set(tags))
                res.update(
                    {
                        "merge_ticket_line_ids": [(6, 0, ticket_line.ids)],
                        "merge_ids": [(6, 0, ticket_ids.ids)],
                        "responsible_user_id": ticket.user_id.id,  # ent_13
                        "partner_id": ticket.partner_id.id,  # ent_13
                        "partner_name": ticket.partner_id.name,  # ent_13
                        "partner_email": ticket.partner_id.email,  # ent_13
                        "ticket_type_id": ticket.ticket_type_id.id,  # ent_13
                        "priority": ticket.priority,  # ent_13
                        # 'tag_ids': ticket.tag_ids.ids, #ent_13
                        "tag_ids": [(6, 0, tags)],  # ent_13
                        "team_id": ticket.team_id.id,  # ent_13
                        "ticket_subject": ticket.name,  # ent_13
                    }
                )
        else:
            raise ValidationError(_("Must be Same Partner or Email or Phone."))
        return res

    # @api.multi
    def action_merge_ticket(self):
        context = dict(self._context or {})
        context.get("active_ids", [])
        desc = ""
        helpdesk_support_obj = self.env["helpdesk.ticket"]
        primary_ticket = self.primary_id
        if self.primary_id:
            if self.is_sure:
                primary_ticket.write({"is_secondry": True})
                for line in self.merge_ids:
                    if line == self.primary_id:
                        pass
                    else:
                        merge_ticket = line
                        d = merge_ticket.description or ""
                        desc += "\n" + d
                        merge_ticket.write(
                            {
                                "primary_ticket_id": primary_ticket.id,
                                "is_secondry": True,
                                "active": False,
                            }
                        )
                primary_ticket.write(
                    {
                        "description": self.primary_id.description or "" + desc,
                        "merge_reason": self.merge_reason,
                    }
                )
                # res = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
                res = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree")
                res = res.sudo().read()[0]
                res["domain"] = str([("id", "=", primary_ticket.id)])
                return res
            else:
                raise ValidationError(_("Please select check box to confirm merge."))
        if self.create_new_ticket:
            add_desc = ""
            for line in self.merge_ids:
                add_desc += "\n" + (line.description or "")
            if self.is_sure:  # ent_13
                tags = []
                tags.extend(self.tag_ids.ids)
                tags = list(set(tags))
                new_ticket_vals = {
                    # 'subject': self.ticket_subject,
                    "name": self.ticket_subject,  # 13_ent
                    "user_id": self.responsible_user_id.id,
                    # 'team_id': self.team_id.id,
                    # 'team_leader_id': self.team_id.leader_id.id,
                    # 'team_leader_id': self.team_id.alias_user_id.id, #13_ent
                    "merge_reason": self.merge_reason,  # ent_13
                    "description": add_desc,  # ent_13
                    "partner_id": self.partner_id.id,  # ent_13
                    "partner_name": self.partner_id.name,  # ent_13
                    "partner_email": self.partner_id.email,  # ent_13
                    "ticket_type_id": self.ticket_type_id.id,  # ent_13
                    "priority": self.priority,  # ent_13
                    "tag_ids": [(6, 0, tags)],  # ent_13
                }
                helpdesk_support_obj.create(new_ticket_vals)
                self.merge_ids.write({"active": False})  # ent_13
            else:  # ent_13
                raise ValidationError(
                    _("Please select check box to confirm create.")
                )  # ent_13


class MergeTicketLine(models.TransientModel):
    _name = "merge.ticket.line"
    _description = "Merge Ticket Line"

    ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Support Ticket",
        readonly=True,
    )
    # subject = fields.Text(
    #     string='Subject',
    #     related='primary_ticket_merge_id.subject', #ent_13
    # )
    subject = fields.Text(
        string="Subject",
    )

    # ticket_merge_id = fields.Many2one(
    #     'ticket.merge.wizard',
    #     string="Merge",
    # ) #ent_13
    primary_ticket_merge_id = fields.Many2one(
        "ticket.merge.wizard",
        string="Merge",
    )

    user_id = fields.Many2one(
        "res.users",
        string="Responsible User",
        related="ticket_id.user_id",
    )  # ent_13
    team_id = fields.Many2one(
        "helpdesk.team",
        string="Support Team",
        related="ticket_id.team_id",
    )  # ent_13
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        related="ticket_id.partner_id",
    )  # ent_13
    partner_name = fields.Char(
        string="Customer Name",
        related="ticket_id.partner_name",
    )  # ent_13
    partner_email = fields.Char(
        string="Customer Email",
        related="ticket_id.partner_email",
    )  # ent_13
    ticket_type_id = fields.Many2one(
        "helpdesk.ticket.type",
        string="Ticket Type",
        related="ticket_id.ticket_type_id",
    )  # ent_13
    priority = fields.Selection(
        TICKET_PRIORITY,
        string="Priority",
        default="0",
        related="ticket_id.priority",
    )  # ent_13
    tag_ids = fields.Many2many(
        "helpdesk.tag",
        string="Tags",
        related="ticket_id.tag_ids",
    )  # ent_13


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
