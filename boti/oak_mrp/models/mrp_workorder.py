from odoo import _, api, fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    mto_origin = fields.Char(
        related="production_id.mto_origin",
        string="MTO Origin",
        readonly=True,
        store=True,
    )
    analytic_account_id = fields.Many2one(
        related="production_id.analytic_account_id",
        string="Analytic Account",
        readonly=True,
        store=True,
    )

    mo_hold = fields.Boolean(
        related="production_id.mo_hold", string="MO on Hold", readonly=True
    )

    mo_hold_reason = fields.Char(
        related="production_id.mo_hold_reason",
        string="MO on Hold Reason",
        readonly=True,
    )

    detail_number = fields.Many2one(
        related="product_id.detail_number_id", string="Detail Number", readonly=True
    )

    machine_id = fields.Many2one("maintenance.equipment", string="Machine")

    employee_id = fields.Many2one("hr.employee", string="Employee")

    note = fields.Text()

    cnc_program = fields.Char(
        string="Program",
        compute="_compute_program_name",
        readonly=True,
    )

    department_id = fields.Many2one(
        string="Department",
        related="workcenter_id.department_id",
        readonly=True,
        store=True,
    )

    department = fields.Char(
        string="Department",
        related="workcenter_id.department_id.name",
        readonly=True,
    )

    @api.depends("workcenter_id")
    def _compute_program_name(self):
        for rec in self:
            cnc_info_line = self.env["product.cnc.info.line"].search(
                [
                    ("product_tmpl_id", "=", rec.product_id.product_tmpl_id.id),
                    ("workcenter_id", "=", rec.workcenter_id.id),
                ]
            )
            rec.cnc_program = cnc_info_line.name

    def write(self, vals):
        for rec in self:
            old_workcenter = rec.workcenter_id.name
            old_workcenter_id = rec.workcenter_id.id
        res = super(MrpWorkorder, self).write(vals)
        # Keep track of requested date change
        if "workcenter_id" in vals:
            if vals["workcenter_id"] != old_workcenter_id:
                new_workcenter = self.env["mrp.workcenter"].search(
                    [("id", "=", vals["workcenter_id"])]
                )
                self.production_id.message_post(
                    body=_(
                        "Workcenter has been changed on "
                        + "Sequence %(sequence)s <br> %(old_wc)s -> %(new_wc)s",
                        sequence=rec.sequence,
                        old_wc=old_workcenter,
                        new_wc=new_workcenter.name,
                    )
                )
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(MrpWorkorder, self).create(vals)
        for val in vals:
            if val.get("sequence"):
                res.production_id.message_post(
                    body=_("New Work Order Created <br> Sequence %s")
                    % (val["sequence"])
                )
        return res
