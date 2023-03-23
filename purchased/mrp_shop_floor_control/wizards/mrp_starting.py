from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpStarting(models.TransientModel):
    _name = "mrp.starting"
    _description = "MRP Starting"

    production_id = fields.Many2one(
        "mrp.production",
        "Production Order",
        domain=[
            ("picking_type_id.active", "=", True),
            ("workorder_ids", "not in", []),
            ("state", "in", ("confirmed", "progress")),
        ],
    )
    workorder_id = fields.Many2one(
        "mrp.workorder",
        "Workorder",
        domain="[('state', 'not in', ['progress','done','cancel']), ('production_id','=',production_id)]",
    )
    company_id = fields.Many2one(
        "res.company", "Company", related="production_id.company_id", readonly=True
    )
    milestone = fields.Boolean("Milestone", related="workorder_id.milestone")
    date_start = fields.Datetime(
        "Start Date", required=True, default=lambda self: fields.datetime.now()
    )

    @api.model
    def default_get(self, fields):
        default = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        if active_id:
            default["production_id"] = active_id
        return default

    @api.onchange("production_id")
    def onchange_production_id(self):
        workorder_domain = [("state", "not in", ["done", "cancel", "progress"])]
        if self.production_id:
            workorder_domain += [("production_id", "=", self.production_id.id)]
            workorder_ids = self.env["mrp.workorder"].search(workorder_domain)
            if workorder_ids:
                if self.workorder_id and self.workorder_id.id not in workorder_ids.ids:
                    self.workorder_id = False

    def do_starting(self):
        self.ensure_one()
        if self.workorder_id.qty_output_prev_wo == 0.0 and not self.milestone:
            raise UserError(_("No WIP qty available"))
        self._set_wo_inprogress(self.workorder_id)

    def _set_wo_inprogress(self, workorder):
        workorder.button_start()
        time_id = self.env["mrp.workcenter.productivity"].search(
            [("workorder_id", "=", workorder.id), ("date_end", "=", False)], limit=1
        )
        if time_id:
            time_id.date_start = self.date_start
