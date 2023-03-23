from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class MrpWorkCenterCapacityLoad(models.Model):
    _name = "mrp.workcenter.capacity.load"
    _description = "Work Center Capacity Load"
    _order = "date_planned DESC"

    workcenter_id = fields.Many2one("mrp.workcenter", "Work Center")
    workorder_id = fields.Many2one("mrp.workorder", "WorkOrder")
    production_id = fields.Many2one(related="workorder_id.production_id")
    product_id = fields.Many2one("product.product", "Product")
    product_qty = fields.Float("Required Quantity")
    product_uom_id = fields.Many2one("uom.uom", "Unit of Measure")
    date_planned = fields.Datetime("Planned Date")
    date_planned_calculated = fields.Datetime(
        "Planned Date", compute="_get_date_planned"
    )
    week_nro = fields.Char("Week Number", compute="_get_week_number", store=True)
    active = fields.Boolean(default=True)
    wo_capacity_requirements = fields.Float("WO Capacity Requirements")
    wc_available_capacity_cal = fields.Float(
        "WC Weekly Available Capacity",
        compute="_calculate_wc_available_capacity_cal",
        store=True,
        group_operator="avg",
    )
    wc_daily_available_capacity_cal = fields.Float(
        "WC Dayly Available Capacity",
        compute="_calculate_wc_available_capacity_cal",
        store=True,
        group_operator="avg",
    )

    @api.depends("date_planned")
    def _calculate_wc_available_capacity_cal(self):
        for record in self:
            record.wc_daily_available_capacity_cal = 0.0
            record.wc_available_capacity_cal = 0.0
            if record.date_planned and record.week_nro:
                monday = datetime.strptime(record.week_nro + "-1", "%Y-%W-%w")
                sunday = monday + timedelta(days=7)
                nro_hours_week = (
                    record.workcenter_id.resource_calendar_id.get_work_hours_count(
                        monday, sunday
                    )
                )
                record.wc_available_capacity_cal = (
                    nro_hours_week
                    * record.workcenter_id.available_capacity
                    * record.workcenter_id.time_efficiency
                    / 100
                )
                date = record.date_planned.date()
                date_planned_start = datetime.strptime(
                    str(date), DEFAULT_SERVER_DATE_FORMAT
                )
                date_planned_end = date_planned_start + timedelta(days=1)
                nro_hours_day = (
                    record.workcenter_id.resource_calendar_id.get_work_hours_count(
                        date_planned_start, date_planned_end
                    )
                )
                record.wc_daily_available_capacity_cal = (
                    nro_hours_day
                    * record.workcenter_id.available_capacity
                    * record.workcenter_id.time_efficiency
                    / 100
                )

    @api.depends("date_planned")
    def _get_week_number(self):
        week = year = False
        for record in self:
            if record.date_planned:
                week = record.date_planned.date().strftime("%V")
                year = record.date_planned.date().strftime("%Y")
            record.week_nro = year + "-" + week

    @api.depends("date_planned")
    def _get_date_planned(self):
        for record in self:
            if record.date_planned:
                record.date_planned_calculated = (
                    record.workcenter_id.resource_calendar_id.plan_hours(
                        0.0, record.date_planned, True
                    )
                )
            else:
                record.date_planned_calculated = False
