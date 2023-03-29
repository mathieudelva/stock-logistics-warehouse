from odoo import fields, models


# Imported Legacy BoM
class MrpBomLegacy(models.Model):
    _name = "mrp.bom.legacy"
    _description = "Legacy Bill of Material"

    name = fields.Char(string="BoM ID")
    description = fields.Char()
    bom_legacy_line_ids = fields.One2many(
        "mrp.bom.line.legacy", "bom_id", "BoM Lines", copy=True
    )
    bomtype = fields.Selection(
        [("0", "Item"), ("1", "Phantom"), ("2", "Pegged Supply"), ("3", "Vendor")],
        string="BOM Type",
        default="0",
        required=True,
        help="Legacy Bill of Material types.",
    )
    is_active = fields.Boolean("Active", compute="_compute_active", store=False)

    def _compute_active(self):
        for rec in self:
            rec.is_active = False
            if (
                self.env["product.template"]
                .search([("default_code", "=", rec.name)])
                .id
            ):
                rec.is_active = True


# Imported AX BoM Lines
class MrpBomLineLegacy(models.Model):
    _name = "mrp.bom.line.legacy"
    _order = "linenum"
    _description = "Legacy AX Bill of Material Lines"
    _check_company_auto = True

    linenum = fields.Float()

    bomtype = fields.Selection(
        [("0", "Item"), ("1", "Phantom"), ("2", "Pegged Supply"), ("3", "Vendor")],
        string="BOM Type",
        default="0",
        required=True,
        help="Legacy AX Bill of Material types.",
    )

    itemid = fields.Char(string="Item")

    itemdesc = fields.Char(string="Description")

    bomqty = fields.Float()

    position = fields.Char()

    oprnum = fields.Char()

    vendid = fields.Char()

    unitid = fields.Char()

    bom_id = fields.Many2one(
        "mrp.bom.legacy",
        "Parent Legacy BoM",
        index=True,
        ondelete="cascade",
        required=True,
    )

    # external recid simplify pre-golive data sync
    external_ref = fields.Char("External Ref #")

    is_active = fields.Boolean("Active", compute="_compute_active", store=False)

    def _compute_active(self):
        for rec in self:
            rec.is_active = False
            if (
                self.env["product.template"]
                .search([("default_code", "=", rec.itemid)])
                .id
            ):
                rec.is_active = True


# Imported AX Routing versions
class MrpRoutingLegacy(models.Model):
    _name = "mrp.routing.legacy"
    _description = "Legacy Routing"

    description = fields.Char()
    itemid = fields.Char()
    name = fields.Char()
    stdorderqty = fields.Float(string="Std Ord Qty")
    active_routing = fields.Boolean(string="Active")
    routing_legacy_line_ids = fields.One2many(
        "mrp.routing.line.legacy", "routing_id", "Routings Operations", copy=True
    )


# Imported AX BoM Lines
class MrpRoutingLineLegacy(models.Model):
    _name = "mrp.routing.line.legacy"
    _order = "oprnum"
    _description = "Legacy AX Routing Operations"
    _check_company_auto = True

    oprnum = fields.Integer(string="Seq")

    work_center = fields.Char(string="WorkCenter")

    wc_description = fields.Char(string="WC Description")

    setuptime = fields.Float(string="Setup")

    stdorderqty = fields.Float(
        string="Std Ord Qty", related="routing_id.stdorderqty", readonly=True
    )

    processtime = fields.Float(string="Process")

    combinedtime = fields.Float(
        string="Combined Time", help="(Setup / Std Ord Qty) + Process"
    )

    plan_time_review_status = fields.Selection(
        [("0", "New"), ("1", "Reviewed")],
        string="Review Status",
        default="0",
        required=True,
        help="Plan time review status.",
    )

    routingtype = fields.Selection(
        [("0", "Standard"), ("1", "Vendor")],
        string="Operation Type",
        default="0",
        required=True,
        help="Legacy AX Routing Operation Types.",
    )

    oprdesc = fields.Char(string="Operation Description")

    routing_id = fields.Many2one(
        "mrp.routing.legacy",
        "Parent Legacy Routing",
        index=True,
        ondelete="cascade",
        required=True,
    )

    # external recid to simlify pre-golive data sync
    external_ref = fields.Char("External Ref #")
