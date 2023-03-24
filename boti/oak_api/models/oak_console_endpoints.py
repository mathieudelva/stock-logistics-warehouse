from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class OakConsoleEndpoints(models.Model):
    _name = "oak.console.endpoints"
    _description = "Endpoints for Oak Worker Console App"

    # Main public call, start wo or new time line
    @api.model
    def oak_wo_start(self, values):
        if not values.get("mo_id"):
            return "mo_id is not set"
        if not values.get("wo_id"):
            return "wo_id is not set"
        if not values.get("date_start"):
            return "date_start is not set"
        if not values.get("user_id"):
            return "user_id is not set"
        self.env.uid = values.get("user_id")
        workorder = self.env["mrp.workorder"].search(
            [
                ("id", "=", values["wo_id"]),
            ],
            limit=1,
        )
        if not workorder.employee_id and values.get("employee_id"):
            workorder.employee_id = values.get("employee_id")
        if not workorder.machine_id and values.get("machine_id"):
            workorder.machine_id = values.get("machine_id")
        time_id = self.env["mrp.workcenter.productivity"].search(
            [
                ("workorder_id", "=", values["wo_id"]),
                ("date_end", "=", False),
                ("date_start", "=", values["date_start"]),
            ],
            limit=1,
        )
        if time_id:
            return self._oak_time_start(values)
        else:
            return self._oak_do_start(values)

    @api.model
    def _oak_do_start(self, values):

        rec = self.env["mrp.starting"].create(
            {
                "production_id": values["mo_id"],
                "workorder_id": values["wo_id"],
                "date_start": values["date_start"],
            }
        )
        rec.do_starting()

        time_id = self.env["mrp.workcenter.productivity"].search(
            [
                ("workorder_id", "=", values["wo_id"]),
                ("date_end", "=", False),
                ("date_start", "=", values["date_start"]),
            ],
            limit=1,
        )
        if time_id:
            return time_id.id

        return "This workorder has already been started"

    @api.model
    def _oak_time_start(self, values):

        time_id = self.env["mrp.workcenter.productivity"].search(
            [
                ("workorder_id", "=", values["wo_id"]),
                ("date_end", "=", False),
                ("user_id", "=", values["user_id"]),
            ],
            limit=1,
        )

        user = self.env["res.users"].search(
            [
                ("id", "=", values["user_id"]),
            ],
            limit=1,
        )

        if time_id:
            return "There is a time entry already for " + user.name

        workorder = self.env["mrp.workorder"].search(
            [
                ("id", "=", values["wo_id"]),
            ],
            limit=1,
        )

        loss_id = self.env["mrp.workcenter.productivity.loss"].search(
            [("loss_type", "=", "productive")], limit=1
        )
        if not len(loss_id):
            raise UserError(
                _(
                    "You need to define productivity loss in the category 'Productivity'."
                )
            )

        rec = self.env["mrp.workcenter.productivity"].create(
            {
                "workorder_id": workorder.id,
                "workcenter_id": workorder.workcenter_id.id,
                "description": _("Time Tracking: %(user)s", user=user.name),
                "loss_id": loss_id[0].id,
                "date_start": values["date_start"],
                "user_id": user.id,
                "company_id": workorder.company_id.id,
            }
        )

        return rec.id

    @api.model
    def oak_wo_confirm(self, values):

        if not values.get("mo_id"):
            return "mo_id is not set"
        if not values.get("wo_id"):
            return "wo_id is not set"
        if not values.get("time_id"):
            return "time_id is not set"
        if not values.get("user_id"):
            return "user_id is not set"
        if not values.get("elapsed"):
            return "elapsed is not set"
        if not values.get("qty_output_wo"):
            return "qty_output_wo is not set"
        if not values.get("company_id"):
            return "company_id is not set"
        self.env.uid = values.get("user_id")
        workorder = self.env["mrp.workorder"].search(
            [
                ("id", "=", values["wo_id"]),
            ],
            limit=1,
        )

        time_id = self.env["mrp.workcenter.productivity"].search(
            [
                ("id", "=", values["time_id"]),
                ("user_id", "=", values["user_id"]),
                ("company_id", "=", values["company_id"]),
            ],
            limit=1,
        )
        if time_id:
            date_end = fields.Datetime.now()
            elapsed = values.get("elapsed")
            date_start = date_end - timedelta(minutes=elapsed)

            rec = self.env["mrp.confirmation"].create(
                {
                    "production_id": values.get("mo_id"),
                    "workorder_id": values.get("wo_id"),
                    "date_start": date_start,
                    "date_end": date_end,
                    "setup_duration": values.get("setup_duration"),
                    "teardown_duration": values.get("teardown_duration"),
                    "working_duration": elapsed,
                    "product_id": workorder.production_id.product_id,
                    "tracking": workorder.production_id.product_id.tracking,
                    "final_lot_id": values.get("final_lot_id"),
                    "qty_production": workorder.qty_production,
                    "qty_output_wo": values.get("qty_output_wo"),
                    "product_uom_id": workorder.production_id.product_uom_id,
                    "user_id": values.get("user_id"),
                    "company_id": values.get("company_id"),
                    "milestone": values.get("milestone"),
                }
            )
            rec.do_confirm()
            time_id.write({"date_start": date_start, "date_end": date_end})
            return time_id.id

        return "No Time Record Found"

    @api.model
    def oak_time_stop(self, values):

        if not values.get("time_id"):
            return "time_id is not set"
        if not values.get("company_id"):
            return "company_id is not set"
        if not values.get("user_id"):
            return "user_id is not set"
        if not values.get("elapsed"):
            return "elapsed is not set"
        self.env.uid = values.get("user_id")
        time_id = self.env["mrp.workcenter.productivity"].search(
            [
                ("id", "=", values["time_id"]),
                ("user_id", "=", values["user_id"]),
                ("company_id", "=", values["company_id"]),
            ],
            limit=1,
        )
        if time_id:
            date_end = fields.Datetime.now()
            elapsed = values.get("elapsed")
            date_start = date_end - timedelta(minutes=elapsed)
            time_id.write({"date_start": date_start, "date_end": date_end})
            return {
                "time_id": time_id.id,
                "date_start": date_start,
                "date_end": date_end,
            }

        return "No Time Record Found"

    @api.model
    def oak_validate_consumption(self, values):

        if not values.get("mo_id"):
            return "mo_id is not set"
        if not values.get("user_id"):
            return "user_id is not set"

        self.env.uid = values.get("user_id")

        production_id = self.env["mrp.production"].search(
            [
                ("id", "=", values["mo_id"]),
            ],
            limit=1,
        )
        if production_id:

            production_id.action_assign()

            components = production_id.move_raw_ids
            if components:
                components_info = {}
                reserve_stock_moves = {}
                for index, component in enumerate(components):
                    components_info[str(index)] = {
                        "move_stock_id": component.id,
                        "product_id": component.product_id.id,
                        "default_code": component.product_id.default_code,
                        "product": component.product_id.name,
                        "qty_demand": component.product_uom_qty,
                        "qty_to_consume": component.quantity_done,
                        "qty_reserved": component.reserved_availability,
                        "product_uom": component.product_uom.name,
                        "is_done": component.is_done,
                    }

                    if (
                        production_id.picking_ids
                        and component.reserved_availability == 0
                        and component.is_done is False
                    ):
                        reserve_stock_moves[str(index)] = {
                            "product_id": component.product_id.id,
                            "default_code": component.product_id.default_code,
                            "qty_demand": component.product_uom_qty,
                            "qty_to_consume": component.quantity_done,
                            "qty_reserved": component.reserved_availability,
                            "product_uom": component.product_uom.name,
                            "message": "Waiting on Stock Moves",
                        }

                return {
                    "components": components_info,
                    "waiting_on_stock": reserve_stock_moves,
                }
            else:
                return "No components in this MO"

        return "No MO Record Found"

    @api.model
    def oak_consume(self, consumption_list):

        if not consumption_list:
            return "Consumption list is empty"

        for values in consumption_list:

            if not values.get("move_id"):
                return "move_id is not set"
            if not values.get("mo_id"):
                return "mo_id is not set"
            if not values.get("product_id"):
                return "product_id is not set"
            if not values.get("qty_to_consume"):
                return "qty_to_consume is not set"
            if not values.get("user_id"):
                return "user_id is not set"
            self.env.uid = values.get("user_id")
            stock_move = self.env["stock.move"].search(
                [
                    ("id", "=", values["move_id"]),
                ],
                limit=1,
            )
            if not stock_move.is_done:
                stock_move.quantity_done = values.get("qty_to_consume")

        production_id = self.env["mrp.production"].search(
            [
                ("id", "=", values["mo_id"]),
            ],
            limit=1,
        )
        if production_id:
            return production_id.action_post_inventory_wip()
        else:
            return "No MO found with given id"

    @api.model
    def oak_mo_close(self, values):
        if not values.get("mo_id"):
            return "mo_id is not set"
        if not values.get("user_id"):
            return "user_id is not set"

        production_id = self.env["mrp.production"].search(
            [
                ("id", "=", values["mo_id"]),
            ],
            limit=1,
        )
        if production_id:
            self.env.uid = values.get("user_id")
            return production_id.button_mark_done()

        return "No MO Record Found"
