from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    PLANNING_MODE = [
        ("F", "Forward"),
        ("B", "Backward"),
    ]

    # Odoo Standard
    lot_producing_id = fields.Many2one(states={"done": [("readonly", True)]})
    user_id = fields.Many2one(states={"done": [("readonly", True)]})
    date_planned_start = fields.Datetime("Planned Start Date")
    # SFC
    planning_mode = fields.Selection(
        PLANNING_MODE,
        "Planning Mode",
        default="F",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]},
        copy=False,
    )
    date_planned_start_pivot = fields.Datetime(
        "Planned Start Pivot Date",
        readonly=True,
        states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]},
        default=lambda self: fields.datetime.now(),
    )
    date_planned_finished_pivot = fields.Datetime(
        "Planned End Pivot Date",
        readonly=True,
        states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]},
        compute="_compute_planned_pivot_finished_date",
        store=True,
    )
    date_planned_start_wo = fields.Datetime(
        "Scheduled Start Date", readonly=True, copy=False
    )
    date_planned_finished_wo = fields.Datetime(
        "Scheduled End Date", readonly=True, copy=False
    )
    date_actual_start_wo = fields.Datetime(
        "Start Date", copy=False, readonly=True, compute="get_actual_dates", store=True
    )
    date_actual_finished_wo = fields.Datetime(
        "End Date", copy=False, readonly=True, compute="get_actual_dates", store=True
    )
    origin = fields.Char(readonly=True, states={"draft": [("readonly", False)]})
    bom_type = fields.Selection(related="bom_id.type", store=True)
    # Time Management
    hours_uom = fields.Many2one("uom.uom", "Hours", compute="_get_uom_hours")
    std_setup_time = fields.Float(
        "Total Setup Time", compute="_get_standard_times", digits=(16, 2)
    )
    std_teardown_time = fields.Float(
        "Total Cleanup Time", compute="_get_standard_times", digits=(16, 2)
    )
    std_working_time = fields.Float(
        "Total Working Time", compute="_get_standard_times", digits=(16, 2)
    )
    std_overall_time = fields.Float(
        "Overall Time", compute="_get_standard_times", digits=(16, 2)
    )
    planned_duration_expected = fields.Float(
        "Planned Times", copy=False, readonly=True, digits=(16, 2)
    )
    unplanned_duration_expected = fields.Float(
        "Unplanned Times", copy=False, readonly=True, digits=(16, 2)
    )
    act_setup_time = fields.Float(
        "Total Setup Time", compute="_get_actual_times", digits=(16, 2)
    )
    act_teardown_time = fields.Float(
        "Total Cleanup Time", compute="_get_actual_times", digits=(16, 2)
    )
    act_working_time = fields.Float(
        "Total Working Time", compute="_get_actual_times", digits=(16, 2)
    )
    act_overall_time = fields.Float(
        "Overall Time", compute="_get_actual_times", digits=(16, 2)
    )
    qty_confirmed = fields.Float(
        "Confirmed Qty", digits="Product Unit of Measure", copy=False, readonly=True
    )
    # Tools
    tool_ids = fields.One2many("mrp.production.tool", "production_id", "Tools")

    @api.onchange(
        "planning_mode",
        "date_planned_start_pivot",
        "product_id",
        "company_id",
        "picking_type_id",
        "bom_id",
    )
    def onchange_planning_mode_forward(self):
        for production in self:
            if production.planning_mode == "F" and production.date_planned_start_pivot:
                production.date_planned_finished_pivot = (
                    production.get_planned_pivot_finished_date(
                        production.date_planned_start_pivot
                    )
                )

    @api.onchange(
        "planning_mode",
        "date_planned_finished_pivot",
        "product_id",
        "company_id",
        "picking_type_id",
        "bom_id",
    )
    def onchange_planning_mode_backward(self):
        for production in self:
            if (
                production.planning_mode == "B"
                and production.date_planned_finished_pivot
            ):
                production.date_planned_start_pivot = (
                    production.get_planned_pivot_start_date(
                        production.date_planned_finished_pivot
                    )
                )

    @api.depends(
        "date_planned_start_pivot",
        "product_id",
        "company_id",
        "picking_type_id",
        "bom_id.type",
        "bom_id",
        "planning_mode",
    )
    def _compute_planned_pivot_finished_date(self):
        for production in self:
            if production.date_planned_start_pivot and production.planning_mode == "F":
                production.date_planned_finished_pivot = (
                    production.get_planned_pivot_finished_date(
                        production.date_planned_start_pivot
                    )
                )
        return True

    @api.constrains("date_planned_start_pivot", "date_planned_finished_pivot")
    def check_dates(self):
        for production in self:
            # if production.date_planned_finished_pivot and production.date_planned_start_pivot and production.date_planned_start_pivot > production.date_planned_finished_pivot:
            #    raise UserError(_("Please check planned pivot dates."))
            if production.state not in ("done", "cancel"):
                production.date_planned_start = production.date_planned_start_pivot
                production.date_planned_finished = (
                    production.date_planned_finished_pivot
                )

    @api.constrains("state")
    def disallocating_tools(self):
        for production in self:
            if production.state == "done":
                for tool in production.tool_ids:
                    tool.tool_id.production_id = False

    def get_planned_pivot_finished_date(self, date_start):
        for production in self:
            # subcontracting
            if production.bom_id.type == "subcontract":
                receipt_move = self.env["stock.move"].search(
                    [("reference", "=", production.procurement_group_id.name)], limit=1
                )
                date_finished = receipt_move.date or datetime.now()
            # produzione
            else:
                date_finished = date_start + relativedelta(
                    days=production.product_id.produce_delay + 1
                )
                if production.company_id.manufacturing_lead > 0:
                    date_finished = date_finished + relativedelta(
                        days=production.company_id.manufacturing_lead + 1
                    )
                if production.picking_type_id.warehouse_id.calendar_id:
                    calendar = production.picking_type_id.warehouse_id.calendar_id
                    date_start = calendar.plan_hours(
                        0.0,
                        date_start,
                        compute_leaves=True,
                        domain=[("time_type", "in", ["leave", "other"])],
                    )
                    date_finished = calendar.plan_days(
                        int(production.product_id.produce_delay) + 1, date_start, True
                    )
                    if production.company_id.manufacturing_lead > 0:
                        date_finished = calendar.plan_days(
                            int(production.company_id.manufacturing_lead) + 1,
                            date_finished,
                            True,
                        )
                if date_finished == date_start:
                    date_finished = date_start + relativedelta(hours=1)
        return date_finished

    def get_planned_pivot_start_date(self, date_finished):
        for production in self:
            date_start = date_finished - relativedelta(
                days=production.product_id.produce_delay + 1
            )
            if production.company_id.manufacturing_lead > 0:
                date_start = date_start - relativedelta(
                    days=production.company_id.manufacturing_lead + 1
                )
            if production.picking_type_id.warehouse_id.calendar_id:
                calendar = production.picking_type_id.warehouse_id.calendar_id
                date_finished = calendar.plan_hours(
                    0.0,
                    date_finished,
                    compute_leaves=True,
                    domain=[("time_type", "in", ["leave", "other"])],
                )
                date_start = calendar.plan_days(
                    -int(production.product_id.produce_delay) - 1, date_finished, True
                )
                if production.company_id.manufacturing_lead > 0:
                    date_start = calendar.plan_days(
                        -int(production.company_id.manufacturing_lead) - 1,
                        date_start,
                        True,
                    )
            if date_finished == date_start:
                date_start = date_finished - relativedelta(hours=1)
        return date_start

    def action_capacity_check(self):
        return {
            "name": _("Capacity Check"),
            "view_mode": "form",
            "res_model": "mrp.capacity.check",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def action_confirm(self):
        res = super().action_confirm()
        for production in self:
            # check working calendar
            warehouse_calendar = production.picking_type_id.warehouse_id.calendar_id
            if not warehouse_calendar:
                raise UserError(
                    _("No working calendar has been assigned to the warehouse: %s")
                    % production.picking_type_id.warehouse_id.name
                )
            # check floating times record exists
            floating_times_id = self.env["mrp.floating.times"].search(
                [("warehouse_id", "=", production.picking_type_id.warehouse_id.id)]
            )
            if not floating_times_id:
                raise UserError(
                    _(
                        "Floating Times record has not been created yet for the warehouse: %s"
                    )
                    % production.picking_type_id.warehouse_id.name
                )
            # gestione MO generale
            production._get_time_durations()
            production.qty_confirmed = production.product_qty
            # update tools
            for tool in production.tool_ids:
                if tool.tool_id.production_id:
                    raise UserError(_("Tool already allocated."))
                tool.tool_id.production_id = production.id
            # subcontracting
            if production.bom_id.type == "subcontract":
                production.move_raw_ids.state = "draft"
                production.move_raw_ids.unlink()
                list_move_raw = []
                if (
                    production.bom_id
                    and production.product_id
                    and production.product_qty > 0
                ):
                    moves_raw_values = production._get_moves_raw_values()
                    for move_raw_values in moves_raw_values:
                        list_move_raw += [Command.create(move_raw_values)]
                    production.move_raw_ids = list_move_raw
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            production = super().create(vals)
            new_tool_ids = []
            for tool in production.bom_id.tool_ids:
                if tool.tool_id.id not in production.tool_ids.tool_id.ids:
                    new_tool_ids.append(
                        [
                            0,
                            0,
                            {
                                "tool_id": tool.tool_id.id,
                            },
                        ]
                    )
            production.tool_ids = new_tool_ids
            return production

    def _get_time_durations(self):
        planned_duration_expected = unplanned_duration_expected = 0.0
        for production in self:
            for workorder in production.workorder_ids.filtered(
                lambda r: r.operation_id.id != False
            ):
                planned_duration_expected += workorder.duration_expected
            production.planned_duration_expected = planned_duration_expected / 60
            for workorder in production.workorder_ids.filtered(
                lambda r: r.operation_id.id == False
            ):
                unplanned_duration_expected += workorder.duration_expected
            production.unplanned_duration_expected = unplanned_duration_expected / 60

    # scheduling
    def schedule_workorders(self):
        max_date_finished = False
        start_date = False
        for production in self:
            production.date_planned_start_wo = False
            production.date_planned_finished_wo = False
            floating_times_id = self.env["mrp.floating.times"].search(
                [("warehouse_id", "=", production.picking_type_id.warehouse_id.id)]
            )
            if not floating_times_id:
                raise UserError(
                    _(
                        "Floating Times record has not been created yet for the warehouse: %s"
                    )
                    % production.picking_type_id.warehouse_id.name
                )
            warehouse_calendar = production.picking_type_id.warehouse_id.calendar_id
            start_date = production.date_planned_start_pivot or fields.Datetime.now()
            # Release production
            release_time = floating_times_id.mrp_release_time
            if release_time > 0.0 and warehouse_calendar:
                start_date = warehouse_calendar.plan_hours(
                    release_time, start_date, True
                )
            # before production
            before_production_time = floating_times_id.mrp_ftbp_time
            if before_production_time > 0.0 and warehouse_calendar:
                start_date = warehouse_calendar.plan_hours(
                    before_production_time, start_date, True
                )
            production.date_planned_start_wo = start_date
            # workorders scheduling
            first_workorder = production.workorder_ids[0]
            sequence_wo = first_workorder.sequence
            first_workorder.date_planned_start_wo = start_date
            calendar = first_workorder.workcenter_id.resource_calendar_id
            if calendar:
                first_workorder.date_planned_start_wo = calendar.plan_hours(
                    0.0, first_workorder.date_planned_start_wo, True
                )
            first_workorder.forwards_scheduling()
            max_date_finished = first_workorder.date_planned_finished_wo
            succ_workorders = (
                self.env["mrp.workorder"]
                .search(
                    [
                        ("production_id", "=", first_workorder.production_id.id),
                        ("state", "in", ("ready", "pending", "waiting")),
                        ("sequence", ">=", sequence_wo),
                        ("id", "!=", first_workorder.id),
                    ]
                )
                .sorted(key=lambda r: r.sequence)
            )
            if succ_workorders:
                current_workorder = first_workorder
                for succ_workorder in succ_workorders:
                    # workorder in parallelo
                    if current_workorder.sequence == succ_workorder.sequence:
                        succ_workorder.date_planned_start_wo = (
                            current_workorder.date_planned_start_wo
                        )
                        succ_workorder.forwards_scheduling()
                    # workorder in sequenza
                    else:
                        succ_workorder.date_planned_start_wo = max_date_finished
                        succ_workorder.forwards_scheduling()
                    max_date_finished = max(
                        succ_workorder.date_planned_finished_wo,
                        current_workorder.date_planned_finished_wo,
                    )
                    current_workorder = succ_workorder
            # after production
            after_production_time = floating_times_id.mrp_ftap_time
            if after_production_time > 0.0 and warehouse_calendar:
                max_date_finished = warehouse_calendar.plan_hours(
                    after_production_time, max_date_finished, True
                )
            production.date_planned_finished_wo = max_date_finished

    def button_plan(self):
        res = super().button_plan()
        for production in self:
            production.schedule_workorders()
        return res

    # delete capacity load
    def button_unplan(self):
        res = super().button_unplan()
        for production in self:
            for workorder in production.workorder_ids:
                workorder.date_planned_start_wo = False
                workorder.date_planned_finished_wo = False
            wo_capacity_ids = self.env["mrp.workcenter.capacity.load"].search(
                [("workorder_id", "in", production.workorder_ids.ids)]
            )
            wo_capacity_ids.unlink()
            production.date_planned_start_wo = False
            production.date_planned_finished_wo = False
        return res

    @api.depends("state")
    def get_actual_dates(self):
        for production in self:
            production.date_actual_start_wo = production.date_actual_finished_wo = False
            if production.workorder_ids:
                if production.state == "done" and production.workorder_ids:
                    workorders = self.env["mrp.workorder"].search(
                        [("production_id", "=", production.id), ("state", "=", "done")]
                    )
                    time_records = self.env["mrp.workcenter.productivity"].search(
                        [("workorder_id", "in", workorders.ids)]
                    )
                    if time_records:
                        production.date_actual_start_wo = time_records.sorted(
                            "date_start"
                        )[0].date_start
                        production.date_actual_finished_wo = time_records.sorted(
                            "date_end"
                        )[-1].date_end
            else:
                if production.state == "confirmed":
                    production.write({"date_actual_start_wo": fields.Datetime.now()})
                if production.state == "done":
                    production.write({"date_actual_finished_wo": fields.Datetime.now()})

    def action_cancel_draft_moves(self):
        for production in self:
            draft_moves = self.env["stock.move"].search(
                [("reference", "=", production.name), ("state", "=", "draft")]
            )
            draft_moves._action_cancel()
            draft_moves.unlink()

    # delete capacity load
    def action_cancel(self):
        for production in self:
            if production.workorder_ids:
                wo_capacity_ids = self.env["mrp.workcenter.capacity.load"].search(
                    [("workorder_id", "in", production.workorder_ids.ids)]
                )
                wo_capacity_ids.unlink()
                if any(
                    workorder.state == "progress"
                    for workorder in production.workorder_ids
                ):
                    raise UserError(_("workorder still running, please close it"))
            for tool in production.tool_ids:
                tool.tool_id.production_id = False
        res = super().action_cancel()
        self.action_cancel_draft_moves()
        return res

    def button_mark_done(self):
        for production in self:
            if production.workorder_ids:
                if not production.is_planned:
                    raise UserError(
                        _("workorders not yet scheduled, please schedule them before")
                    )
                if any(
                    workorder.state not in ("done", "cancel")
                    for workorder in production.workorder_ids
                ):
                    raise UserError(
                        _("workorders not yet processed, please close them before")
                    )
                if production.picking_type_id.active:
                    if any(
                        picking_id.state not in ("done", "cancel", "waiting")
                        for picking_id in production.picking_ids
                    ):
                        raise UserError(
                            _(
                                "components picking not yet processed, please close or cancel it"
                            )
                        )
        res = super().button_mark_done()
        self.action_cancel_draft_moves()
        return res

    @api.constrains("date_planned_start_pivot", "date_planned_finished_pivot", "state")
    def _align_picking_moves_dates(self):
        for production in self:
            production._align_stock_moves_dates()
            production._align_pickings_dates()

    def _align_stock_moves_dates(self):
        for production in self:
            if production.move_finished_ids and production.date_planned_finished_pivot:
                # production.move_finished_ids.write({'date': production.date_planned_finished_pivot, 'date_deadline': production.date_planned_finished_pivot})
                production.move_finished_ids.date = (
                    production.date_planned_finished_pivot
                )
                production.move_finished_ids.date_deadline = (
                    production.date_planned_finished_pivot
                )
            if production.move_raw_ids and production.date_planned_start_pivot:
                production.move_raw_ids.write(
                    {
                        "date": production.date_planned_start_pivot,
                        "date_deadline": production.date_planned_start_pivot,
                    }
                )

    def _align_pickings_dates(self):
        for production in self:
            if (
                production.date_planned_finished_pivot
                and production.date_planned_start_pivot
            ):
                for picking in production.picking_ids.filtered(
                    lambda r: r.state not in ("done", "cancel")
                ):
                    picking.write(
                        {
                            "scheduled_date": production.date_planned_start_pivot,
                            "date_deadline": production.date_planned_start_pivot,
                        }
                    )
                if (
                    production.picking_type_id.warehouse_id.manufacture_steps
                    == "pbm_sam"
                ):
                    for picking in production.picking_ids.filtered(
                        lambda r: r.state not in ("done", "cancel")
                        and r.location_dest_id == production.location_src_id
                    ):
                        picking.write(
                            {
                                "scheduled_date": production.date_planned_start_pivot,
                                "date_deadline": production.date_planned_start_pivot,
                            }
                        )
                    for picking in production.picking_ids.filtered(
                        lambda r: r.state not in ("done", "cancel")
                        and r.location_id == production.location_dest_id
                    ):
                        picking.write(
                            {
                                "scheduled_date": production.date_planned_finished_pivot,
                                "date_deadline": production.date_planned_finished_pivot,
                            }
                        )

    @api.depends("workorder_ids.state")
    def _get_actual_times(self):
        act_setup_time = act_teardown_time = act_working_time = act_overall_time = 0.0
        for workorder in self.workorder_ids.filtered(lambda r: r.state == "done"):
            for time in workorder.time_ids:
                act_setup_time += time.setup_duration
                act_working_time += time.working_duration
                act_teardown_time += time.teardown_duration
                act_overall_time += time.overall_duration
        self.act_setup_time = act_setup_time / 60
        self.act_teardown_time = act_teardown_time / 60
        self.act_working_time = act_working_time / 60
        self.act_overall_time = act_overall_time / 60

    def _get_uom_hours(self):
        self.hours_uom = self.env.ref(
            "uom.product_uom_hour", raise_if_not_found=False
        ).id

    @api.depends("bom_id", "product_uom_qty")
    def _get_standard_times(self):
        std_setup_time = std_teardown_time = std_working_time = 0.0
        for production in self:
            for operation in production.bom_id.operation_ids:
                std_setup_time += operation.workcenter_id.time_start
                std_teardown_time += operation.workcenter_id.time_stop
                cycle_number = float_round(
                    production.product_uom_qty
                    / operation.workcenter_id._get_capacity(production.product_id),
                    precision_digits=0,
                    rounding_method="UP",
                )
                time_cycle = operation.time_cycle
                std_working_time += (
                    cycle_number
                    * time_cycle
                    * 100.0
                    / operation.workcenter_id.time_efficiency
                ) / production.bom_id.product_qty
            production.std_setup_time = std_setup_time / 60
            production.std_teardown_time = std_teardown_time / 60
            production.std_working_time = std_working_time / 60
            production.std_overall_time = (
                std_setup_time + std_teardown_time + std_working_time
            ) / 60

    @api.onchange("bom_id")
    def _onchange_bom_id(self):
        if (
            self.bom_id
            and self.bom_id.picking_type_id
            and self.bom_id.picking_type_id != self.picking_type_id
        ):
            raise UserError(_("BoM Operazione Type is not allowed."))

    @api.onchange("product_id", "picking_type_id", "company_id")
    def _onchange_product_id_picking_type_id(self):
        if not self.product_id:
            self.bom_id = False
        elif (
            not self.bom_id
            or self.bom_id.product_tmpl_id != self.product_tmpl_id
            or (self.bom_id.product_id and self.bom_id.product_id != self.product_id)
            or self.bom_id.picking_type_id != self.picking_type_id
        ):
            bom = self.env["mrp.bom"]._bom_find(
                self.product_id,
                picking_type=self.picking_type_id,
                company_id=self.company_id.id,
                bom_type="normal",
            )[self.product_id]
            if bom:
                self.bom_id = bom.id
                self.product_qty = self.bom_id.product_qty
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id

    ## change standard
    def _generate_backorder_productions(self, close_mo=True):
        backorders = self.env["mrp.production"]
        for production in self:
            if production.backorder_sequence == 0:  # Activate backorder naming
                production.backorder_sequence = 1
            production.name = self._get_name_backorder(
                production.name, production.backorder_sequence
            )
            backorder_mo = production.copy(default=production._get_backorder_mo_vals())
            if close_mo:
                production.move_raw_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                ).write(
                    {
                        "raw_material_production_id": backorder_mo.id,
                    }
                )
                production.move_finished_ids.filtered(
                    lambda m: m.state not in ("done", "cancel")
                ).write(
                    {
                        "production_id": backorder_mo.id,
                    }
                )
            else:
                new_moves_vals = []
                for move in production.move_raw_ids | production.move_finished_ids:
                    if not move.additional:
                        qty_to_split = (
                            move.product_uom_qty
                            - move.unit_factor * production.qty_producing
                        )
                        qty_to_split = move.product_uom._compute_quantity(
                            qty_to_split,
                            move.product_id.uom_id,
                            rounding_method="HALF-UP",
                        )
                        move_vals = move._split(qty_to_split)
                        if not move_vals:
                            continue
                        if move.raw_material_production_id:
                            move_vals[0]["raw_material_production_id"] = backorder_mo.id
                        else:
                            move_vals[0]["production_id"] = backorder_mo.id
                        new_moves_vals.append(move_vals[0])
                self.env["stock.move"].create(new_moves_vals)
            backorders |= backorder_mo

            planned_duration_expected = unplanned_duration_expected = 0.0
            for workorder in production.workorder_ids.filtered(
                lambda r: r.operation_id.id != False
            ):
                workorder.duration_expected = workorder._get_duration_expected()
                planned_duration_expected += workorder.duration_expected
            production.planned_duration_expected = planned_duration_expected / 60
            for workorder in production.workorder_ids.filtered(
                lambda r: r.operation_id.id == False
            ):
                workorder.duration_expected = workorder._get_duration_expected()
                unplanned_duration_expected += workorder.duration_expected
            production.unplanned_duration_expected = unplanned_duration_expected / 60

            planned_duration_expected = unplanned_duration_expected = 0.0
            for workorder in backorder_mo.workorder_ids.filtered(
                lambda r: r.operation_id.id != False
            ):
                workorder.duration_expected = workorder._get_duration_expected()
                planned_duration_expected += workorder.duration_expected
            backorder_mo.planned_duration_expected = planned_duration_expected / 60
            for workorder in backorder_mo.workorder_ids.filtered(
                lambda r: r.operation_id.id == False
            ):
                workorder.duration_expected = workorder._get_duration_expected()
                unplanned_duration_expected += workorder.duration_expected
            backorder_mo.unplanned_duration_expected = unplanned_duration_expected / 60

        # As we have split the moves before validating them, we need to 'remove' the excess reservation
        if not close_mo:
            self.move_raw_ids.filtered(lambda m: not m.additional)._do_unreserve()
            self.move_raw_ids.filtered(lambda m: not m.additional)._action_assign()
        backorders.action_confirm()
        backorders.action_assign()

        # Remove the serial move line without reserved quantity. Post inventory will assigned all the non done moves
        # So those move lines are duplicated.
        backorders.move_raw_ids.move_line_ids.filtered(
            lambda ml: ml.product_id.tracking == "serial" and ml.product_qty == 0
        ).unlink()

        for old_wo, wo in zip(self.workorder_ids, backorders.workorder_ids):
            wo.qty_produced = max(old_wo.qty_produced - old_wo.qty_producing, 0)
            if wo.product_tracking == "serial":
                wo.qty_producing = 1
            else:
                wo.qty_producing = wo.qty_remaining

        backorders.write(
            {
                "qty_producing": 0.0,
            }
        )

        return backorders

    @api.depends(
        "move_raw_ids.state",
        "move_raw_ids.quantity_done",
        "move_finished_ids.state",
        "workorder_ids.state",
        "product_qty",
        "qty_producing",
    )
    def _compute_state(self):
        for production in self:
            if not production.state or not production.product_uom_id:
                production.state = "draft"
            elif production.state == "cancel" or (
                production.move_finished_ids
                and all(move.state == "cancel" for move in production.move_finished_ids)
            ):
                production.state = "cancel"
            elif (
                production.state == "done"
                or (
                    production.move_raw_ids
                    and all(
                        move.state in ("cancel", "done")
                        for move in production.move_raw_ids
                    )
                )
                and all(
                    move.state in ("cancel", "done")
                    for move in production.move_finished_ids
                )
            ):
                production.state = "done"
            elif production.workorder_ids and all(
                wo_state in ("done", "cancel")
                for wo_state in production.workorder_ids.mapped("state")
            ):
                production.state = "to_close"
            elif (
                not production.workorder_ids
                and float_compare(
                    production.qty_producing,
                    production.product_qty,
                    precision_rounding=production.product_uom_id.rounding,
                )
                >= 0
            ):
                production.state = "to_close"
            elif any(
                wo_state in ("progress", "done")
                for wo_state in production.workorder_ids.mapped("state")
            ):
                production.state = "progress"
            elif production.product_uom_id and not production.qty_producing == 0.0:
                production.state = "progress"
            elif any(not move.quantity_done == 0.0 for move in production.move_raw_ids):
                production.state = "progress"

    def _action_confirm_mo_backorders(self):
        self.workorder_ids.unlink()
        workorders_values = workorders_list = []
        for operation in self.bom_id.operation_ids:
            workorders_values += [
                {
                    "name": operation.name,
                    "production_id": self.id,
                    "workcenter_id": operation.workcenter_id.id,
                    "product_uom_id": self.product_uom_id.id,
                    "operation_id": operation.id,
                    "state": "pending",
                }
            ]
        for workorder_values in workorders_values:
            self.env["mrp.workorder"].create(workorder_values)
        return super()._action_confirm_mo_backorders()


class MrpOrderTools(models.Model):
    _name = "mrp.production.tool"
    _description = "Production Order Tools"

    tool_id = fields.Many2one("mrp.tool", "Tools", required=True)
    production_id = fields.Many2one("mrp.production", "Manufacturing Order")
    other_production_id = fields.Many2one(
        "mrp.production",
        "Allocated Manufacturing Order",
        readonly=True,
        related="tool_id.production_id",
    )
    date_next_calibration = fields.Datetime(
        "Next Calibration Date",
        readonly=True,
        related="tool_id.date_next_calibration",
        store=True,
    )
    unallocating_allowed = fields.Boolean(
        compute="_get_unallocating_allowed", store=True
    )

    @api.constrains("tool_id")
    def check_tool_id(self):
        for record in self:
            for tool in record.production_id.tool_ids:
                tools = self.search(
                    [
                        ("production_id", "=", record.production_id.id),
                        ("tool_id", "=", record.tool_id.id),
                    ]
                )
        if len(tools) > 1:
            raise UserError(_("Tool already entered"))

    def unallocating_tool(self):
        for record in self:
            if record.tool_id.production_id.id == record.production_id.id:
                record.tool_id.production_id = False
            else:
                raise UserError(_("Unallocating is not allowed."))

    @api.depends("production_id", "tool_id.production_id")
    def _get_unallocating_allowed(self):
        for record in self:
            record.unallocating_allowed = False
            if (
                not record.tool_id.production_id
                or record.tool_id.production_id.id != record.production_id.id
            ):
                record.unallocating_allowed = True

    ##tool attachment
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [
            "&",
            ("res_model", "=", "mrp.tool"),
            ("res_id", "in", self.tool_id.ids),
        ]
        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "ir.attachment",
            #'views': [(self.env.ref('mrp_shop_floor_control.view_ir_attachment_kanban').id, "kanban")],
            "view_mode": "kanban",
            "view_id": False,
            "type": "ir.actions.act_window",
            "limit": 80,
            "context": "{'default_res_model': '%s','default_res_id': %d, 'create': 0}"
            % (self._name, self.id),
        }
