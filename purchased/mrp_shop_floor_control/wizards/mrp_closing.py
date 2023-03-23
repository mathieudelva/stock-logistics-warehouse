from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpClosing(models.TransientModel):
    _name = "mrp.closing"
    _description = "MRP Closing"

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
        domain="[('state', '=', 'progress'), ('production_id','=', production_id)]",
    )
    company_id = fields.Many2one(
        "res.company", "Company", related="production_id.company_id", readonly=True
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
        workorder_domain = [("state", "=", "progress")]
        if self.production_id:
            workorder_domain += [("production_id", "=", self.production_id.id)]
            workorder_ids = self.env["mrp.workorder"].search(workorder_domain)
            if workorder_ids:
                if self.workorder_id and self.workorder_id.id not in workorder_ids.ids:
                    self.workorder_id = False

    def do_closing(self):
        if any(time_id.date_end == False for time_id in self.workorder_id.time_ids):
            raise UserError(
                _("Time record still open, please confirm workorder to close it")
            )
        prev_workorders_progress = self.production_id.workorder_ids.filtered(
            lambda x: (
                x.sequence < self.workorder_id.sequence and x.state == "progress"
            )
        )
        if prev_workorders_progress:
            raise UserError(_("Previous workorders still in progress"))
        closed_time_id = self.env["mrp.workcenter.productivity"].search(
            [("workorder_id", "=", self.workorder_id.id), ("date_end", "!=", False)],
            limit=1,
        )
        if not closed_time_id:
            raise UserError(_("No time record, please confirm workorder before"))
        self.workorder_id.button_start()
        time_id = self.env["mrp.workcenter.productivity"].search(
            [("workorder_id", "=", self.workorder_id.id), ("date_end", "=", False)],
            limit=1,
        )
        self.workorder_id.button_finish()
        time_values = {
            "date_start": fields.Datetime.now(),
            "date_end": fields.Datetime.now(),
            "user_id": self.env.user.id,
            "final_confirmation": True,
        }
        time_id.write(time_values)
        # chiusura WO precedenti alla milestone
        if self.workorder_id.milestone:
            prev_workorders = self.production_id.workorder_ids.filtered(
                lambda x: x.sequence < self.workorder_id.sequence
            )
            for prev_workorder in prev_workorders:
                if prev_workorder.state in ("ready", "pending", "waiting"):
                    qty = self.workorder_id.qty_output_wo
                    self.env["mrp.confirmation"].do_previous_workorders_confirmation(
                        prev_workorder,
                        qty,
                        self.workorder_id.date_actual_start_wo,
                        self.workorder_id.date_actual_finished_wo,
                    )
            else:
                if any(
                    prev_workorder.state not in ("done", "cancel")
                    for prev_workorder in prev_workorders
                ):
                    raise UserError(
                        _("previous workorders not yet closed or cancelled")
                    )
        return True
