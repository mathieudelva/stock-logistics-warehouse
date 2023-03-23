from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpIndependentDemand(models.Model):
    _name = "mrp.demand"
    _description = "MRP Independent Demand"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "mrp_parameter_id, date_requested, id"

    STATE_SELECTION = [
        ("draft", "Draft"),
        ("cancel", "Cancelled"),
        ("done", "Approved"),
    ]

    mrp_parameter_id = fields.Many2one(
        "mrp.parameter",
        "Planning Parameters",
        index=True,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain=[("demand_indicator", "not in", ("00", "20"))],
    )
    product_id = fields.Many2one(
        "product.product",
        "Product",
        readonly=True,
        related="mrp_parameter_id.product_id",
        store=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        "UoM",
        readonly=True,
        related="product_id.product_tmpl_id.uom_id",
        store=True,
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        "Warehouse",
        readonly=True,
        related="mrp_parameter_id.warehouse_id",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        readonly=True,
        related="mrp_parameter_id.company_id",
        store=True,
    )
    user_id = fields.Many2one(
        "res.users",
        "Responsible Planner",
        related="mrp_parameter_id.user_id",
        store=True,
    )
    state = fields.Selection(
        STATE_SELECTION,
        "Status",
        index=True,
        required=True,
        readonly=True,
        copy=False,
        default="draft",
    )
    date_requested = fields.Datetime(
        "Requested Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_planned = fields.Datetime(
        "Planned Date", compute="_get_planned_date", store=True
    )
    planned_qty = fields.Float(
        "Planned Qty",
        required=True,
        digits="Product Unit of Measure",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=1.0,
    )
    mrp_qty = fields.Float("MRP Qty", digits="Product Unit of Measure", readonly=True)
    active = fields.Boolean(default=True)

    @api.depends("mrp_parameter_id", "date_requested")
    def _get_planned_date(self):
        date_planned = False
        for record in self:
            if record.date_requested and record.product_id:
                customer_lt = (
                    record.product_id.sale_delay
                    or record.product_id.product_tmpl_id.sale_delay
                    or 1.0
                )
                # date_planned = record.warehouse_id.calendar_id.plan_days(-int(customer_lt), record.date_requested, True)
                date_planned = record.date_requested - timedelta(days=customer_lt)
            record.date_planned = date_planned

    @api.constrains("warehouse_id")
    def check_working_calendar(self):
        if self.warehouse_id and not self.warehouse_id.calendar_id:
            raise UserError(
                _("no working calendar has been set on the warehouse: please check %s")
                % self.warehouse_id.name
            )

    @api.constrains("warehouse_id")
    def check_demand_indicator(self):
        for record in self:
            if record.mrp_parameter_id.demand_indicator in ("20", "00"):
                raise UserError(
                    _("no demand management has been activated for the product %s")
                    % record.mrp_parameter_id.product_id.name
                )

    @api.constrains("planned_qty")
    def check_planned_quantity(self):
        if self.planned_qty <= 0.0:
            raise UserError(_("The Planned Quantity has to be positive!"))

    def button_done(self):
        if any(record.state != "draft" for record in self):
            raise UserError(_("Approval is possible in draft status only"))
        for record in self:
            record.write({"state": "done", "mrp_qty": record.planned_qty})

    def button_draft(self):
        if any(record.state != "done" for record in self):
            raise UserError(_("Reset is possible in approved status only"))
        for record in self:
            if record.planned_qty != record.mrp_qty and record.mrp_qty > 0:
                raise UserError(
                    _(
                        "Reset is not possible because the demand item has not yet consumed"
                    )
                )
            record.write({"state": "draft", "mrp_qty": 0.0})

    def button_force_mrp_qty(self):
        if any(record.state != "done" for record in self):
            raise UserError(_("MRP Qty can be forced to zero in approved status only"))
        for record in self:
            record.mrp_qty = 0

    def button_cancel(self):
        if any(record.state != "draft" for record in self):
            raise UserError(_("Cancel is possible in draft status only"))
        for record in self:
            record.write({"state": "cancel"})

    def unlink(self):
        if any(record.state != "cancel" for record in self):
            raise UserError(_("Deletion is possible in cancel status only"))
        res = super().unlink()
        return res
