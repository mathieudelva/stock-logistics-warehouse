from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # incident fields
    show_incident_fields = fields.Boolean(related="team_id.show_incident_fields")
    is_warranty = fields.Boolean(string="Warranty", default=False)
    ref_product = fields.Many2one(
        "product.product", "Machine", help="Reference Machine or Product"
    )
    ref_product_legacy = fields.Text(
        "Opt: Legacy Machine", help="Reference Legacy Machine or Product"
    )
    ref_saleorder = fields.Many2one(
        "sale.order", "Ref Sales Order", help="Reference Sales Order"
    )
    ref_saleorder_legacy = fields.Char(
        string="Opt: Legacy Sales Order", help="Sales Order not in system."
    )
    incident_cause = fields.Many2one("helpdesk.incident.cause", help="Incident Cause")

    incident_source = fields.Many2one(
        "helpdesk.incident.source", help="Incident Source"
    )

    case_item_ids = fields.One2many(
        "helpdesk.case.items", "case_item_id", "Case Items", copy=True
    )

    # show searchable externalid if exists
    ext_ref = fields.Char(
        string="External ID", compute="_compute_ext_id", compute_sudo=True, store=True
    )

    @api.depends("show_incident_fields")
    def _compute_ext_id(self):
        for record in self:
            domain = [
                "&",
                ("res_id", "=", record.id),
                ("model", "=", "helpdesk.ticket"),
            ]
            ext_ids = record.env["ir.model.data"].search(domain, limit=1).ids
            if ext_ids:
                rec = record.env["ir.model.data"].browse(ext_ids[0])
                if rec:
                    record.ext_ref = rec.module + "." + rec.name
