from datetime import datetime, timedelta

from odoo import _, api, fields, models


class MrpCapacityCheck(models.TransientModel):
    _name = "mrp.capacity.check"
    _description = "MRP Capacity Check"

    def _default_production_id(self):
        return self.env["mrp.production"].browse(self.env.context.get("active_id"))

    production_id = fields.Many2one(
        "mrp.production",
        "Manufacturing Order",
        default=lambda self: self._default_production_id(),
        readonly=True,
    )
    capacity_item_ids = fields.One2many(
        "mrp.capacity.check.item", "check_id", string="Capacity Items", readonly=True
    )

    @api.onchange("production_id")
    def get_records(self):
        weeks = []
        workcenters = self.env["mrp.workcenter"].search(
            [("id", "in", self.production_id.workorder_ids.workcenter_id.ids)]
        )
        result = {wc: {} for wc in workcenters.ids}
        domain = [("production_id", "=", self.production_id.id)]
        res = self.env["mrp.workcenter.capacity.load"].read_group(
            domain,
            ["workcenter_id", "week_nro", "wo_capacity_requirements"],
            ["workcenter_id", "week_nro"],
            lazy=False,
        )
        for res_group in res:
            result[res_group["workcenter_id"][0]][res_group["week_nro"]] = res_group[
                "wo_capacity_requirements"
            ]
        for workcenter in workcenters:
            for week, req in result[workcenter.id].items():
                id_created_item = self.env["mrp.capacity.check.item"].create(
                    {
                        "workcenter_id": workcenter.id,
                        "week_nro": week,
                        "wo_capacity_requirements": req,
                        "check_id": self.id,
                    }
                )
                weeks.append(week)
        for week in weeks:
            res_all = self.env["mrp.workcenter.capacity.load"].read_group(
                [("workcenter_id", "in", workcenters.ids), ("week_nro", "=", week)],
                ["workcenter_id", "wo_capacity_requirements"],
                ["workcenter_id"],
            )
            result_all = {wc: {} for wc in workcenters.ids}
            for res_group_all in res_all:
                result_all[res_group_all["workcenter_id"][0]] = res_group_all[
                    "wo_capacity_requirements"
                ]
            for workcenter in workcenters:
                check_item = self.env["mrp.capacity.check.item"].search(
                    [("workcenter_id", "=", workcenter.id), ("week_nro", "=", week)]
                )
                if check_item:
                    check_item.write(
                        {
                            "all_wo_capacity_requirements": result_all.get(
                                workcenter.id, 0.0
                            )
                        }
                    )
        return self._reopen_form()

    def _reopen_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }


class MrpCapacityCheckItem(models.TransientModel):
    _name = "mrp.capacity.check.item"
    _description = "MRP Capacity Check Item"

    check_id = fields.Many2one("mrp.capacity.check", readonly=True)
    workcenter_id = fields.Many2one("mrp.workcenter", "Work Center")
    week_nro = fields.Char("Week Number")
    # week_nro_2 = fields.Char('Week Number', compute='_get_week_number_2')
    wo_capacity_requirements = fields.Float("WO Capacity Requirements (Hours)")
    wc_available_capacity_cal = fields.Float(
        "WC Weekly Available Capacity",
        compute="_calculate_wc_available_capacity_cal",
        store=True,
    )
    all_wo_capacity_requirements = fields.Float("All WO Capacity Requirements (Hours)")
    wc_capacity_load = fields.Float("WC Capacity Load %", compute="_get_wc_capacity")
    wc_remaining_capacity = fields.Float(
        "WC Remaining Capacity", compute="_get_wc_capacity"
    )

    @api.depends("week_nro")
    def _calculate_wc_available_capacity_cal(self):
        for record in self:
            record.wc_available_capacity_cal = False
            if record.week_nro:
                monday = datetime.strptime(record.week_nro + "-1", "%Y-%W-%w")
                sunday = monday + timedelta(days=7)
                nro_hours = (
                    record.workcenter_id.resource_calendar_id.get_work_hours_count(
                        monday, sunday
                    )
                )
                record.wc_available_capacity_cal = (
                    nro_hours
                    * record.workcenter_id.default_capacity
                    * record.workcenter_id.time_efficiency
                    / 100
                )

    # @api.depends('week_nro')
    # def _get_week_number_2(self):
    #    for record in self:
    #        record.week_nro_2 = False
    #        if record.week_nro:
    #            monday = datetime.strptime(record.week_nro + '-1', "%Y-%W-%w") + timedelta(days=7)
    #            week = monday.date().strftime("%V")
    #            year = monday.date().strftime("%Y")
    #            record.week_nro_2 = year + "-" + week

    @api.depends("all_wo_capacity_requirements", "wc_available_capacity_cal")
    def _get_wc_capacity(self):
        for record in self:
            if record.wc_available_capacity_cal:
                record.wc_capacity_load = (
                    record.all_wo_capacity_requirements
                    / record.wc_available_capacity_cal
                ) * 100
            else:
                record.wc_capacity_load = 0.0
            record.wc_remaining_capacity = (
                record.wc_available_capacity_cal - record.all_wo_capacity_requirements
            )

    def open_pivot_info(self):
        context = {
            "default_workcenter_id": self.workcenter_id.id,
        }
        domain = [("workcenter_id", "=", self.workcenter_id.id)]
        return {
            "name": _("Workcenter Capacity Elaluations"),
            "view_mode": "pivot",
            "res_model": "mrp.workcenter.capacity.load",
            "type": "ir.actions.act_window",
            "context": context,
            "domain": domain,
            "target": "fullscreen",
        }
