from random import randint

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpToolTags(models.Model):
    _name = "mrp.tool.tags"
    _description = "MRP Tool Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Name", required=True)
    color = fields.Integer(string="Color", default=_get_default_color)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists!"),
    ]


class MrpTool(models.Model):
    _name = "mrp.tool"
    _description = "Production Tool"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]

    name = fields.Char("Tool Name", required=True)
    tag_ids = fields.Many2many("mrp.tool.tags", string="Tags")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company, readonly=True
    )
    production_id = fields.Many2one(
        "mrp.production", "Allocated Manufacturing Order", readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    active = fields.Boolean("Active", default=True)
    tool_number = fields.Char("Tool Code")
    model = fields.Char("Model Code")
    serial = fields.Char("Serial no.")
    asset_id = fields.Char("Asset Number")
    purchase_value = fields.Float("Purchase Value", tracking=True)
    manufacturer_id = fields.Many2one("res.partner", "Manufacturer")
    warranty_start_date = fields.Date("Warranty Start Date")
    warranty_end_date = fields.Date("Warranty End Date")
    vendor_id = fields.Many2one("res.partner", "Vendor")
    purchase_date = fields.Date("Purchase Date")
    doc_count = fields.Integer(
        "Number of attached documents", compute="_compute_attached_docs_count"
    )
    note = fields.Text("Internal Notes")
    date_next_calibration = fields.Datetime("Next Calibration Date")

    def unallocating_tool(self):
        for record in self:
            record.production_id = False

    @api.constrains("name", "tool_number")
    def check_unique(self):
        tool_name = self.search([("name", "=", self.name)])
        if len(tool_name) > 1:
            raise UserError(_("Tool Name already exists"))
        tool_number = self.env["mrp.tool"].search([("name", "=", self.tool_number)])
        if len(tool_number) > 1:
            raise UserError(_("Tool Number already exists"))

    @api.constrains("warranty_start_date", "warranty_end_date")
    def _check_warranty_dates(self):
        if (self.warranty_start_date and self.warranty_end_date) and (
            self.warranty_start_date >= self.warranty_end_date
        ):
            raise UserError(_("check validity dates"))

    def _compute_attached_docs_count(self):
        attachment = self.env["ir.attachment"]
        for tool in self:
            tool.doc_count = attachment.search_count(
                ["&", ("res_model", "=", "mrp.tool"), ("res_id", "=", tool.id)]
            )

    def attachment_tree_view(self):
        self.ensure_one()
        domain = ["&", ("res_model", "=", "mrp.tool"), ("res_id", "in", self.ids)]
        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "ir.attachment",
            "view_id": False,
            "view_mode": "kanban,tree,form",
            "type": "ir.actions.act_window",
            "limit": 80,
            "context": "{'default_res_model': '%s','default_res_id': %d}"
            % (self._name, self.id),
        }
