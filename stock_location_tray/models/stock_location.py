# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict
from odoo import _, api, exceptions, fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized


class StockLocation(models.Model):
    _inherit = "stock.location"

    tray_type_id = fields.Many2one(
        comodel_name="stock.location.tray.type", ondelete="restrict"
    )
    cell_in_tray_type_id = fields.Many2one(
        string="Cell Tray Type",
        related="location_id.tray_type_id",
        readonly=True,
    )
    tray_cell_contains_stock = fields.Boolean(
        compute="_compute_tray_cell_contains_stock",
        help="Used to know if a cell of a Tray location is empty.",
    )
    tray_matrix = Serialized(string="Cells", compute="_compute_tray_matrix")
    cell_name_format = fields.Char(
        string="Name Format for Cells",
        default=lambda self: self._default_cell_name_format(),
        help="Cells sub-locations generated in a tray will be named"
        " after this format. Replacement fields between curly braces are used"
        " to inject positions. {x}, {y}, and {z} will be replaced by their"
        " corresponding position. Complex formatting (such as padding, ...)"
        " can be done using the format specification at "
        " https://docs.python.org/2/library/string.html#formatstrings",
    )

    def _default_cell_name_format(self):
        return "x{x:0>2}y{y:0>2}"

    @api.depends("quant_ids.quantity")
    def _compute_tray_cell_contains_stock(self):
        for location in self:
            if not location.cell_in_tray_type_id:
                # we skip the others only for performance
                continue
            quants = location.quant_ids.filtered(lambda r: r.quantity > 0)
            location.tray_cell_contains_stock = bool(quants)

    @api.depends(
        "quant_ids.quantity", "tray_type_id", "location_id.tray_type_id"
    )
    def _compute_tray_matrix(self):
        for location in self:
            if not (location.tray_type_id or location.cell_in_tray_type_id):
                continue
            location.tray_matrix = {
                "selected": location._tray_cell_coords(),
                "cells": location._tray_cell_matrix(),
            }

    @api.multi
    def action_tray_matrix_click(self, coordX, coordY):
        self.ensure_one()
        if self.cell_in_tray_type_id:
            tray = self.location_id
        else:
            tray = self
        location = self.search(
            [
                ("id", "child_of", tray.ids),
                # we receive positions counting from 0 but they are stored
                # in the "human" format starting from 1
                ("posx", "=", coordX + 1),
                ("posy", "=", coordY + 1),
            ]
        )
        location.ensure_one()
        view = self.env.ref("stock.view_location_form")
        action = self.env.ref("stock.action_location_form").read()[0]
        action.update(
            {
                "res_id": location.id,
                "view_mode": "form",
                "view_type": "form",
                "view_id": view.id,
                "views": [(view.id, "form")],
            }
        )
        return action

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_tray_sublocations()
        return records

    def _check_before_add_tray_type(self):
        if not self.tray_type_id and self.child_ids:
            raise exceptions.UserError(
                _(
                    "Location %s has sub-locations, it cannot be converted"
                    " to a tray."
                )
                % (self.display_name)
            )

    @api.multi
    def write(self, vals):
        for location in self:
            trays_to_update = False
            if "tray_type_id" in vals:
                location._check_before_add_tray_type()
                new_tray_type_id = vals.get("tray_type_id")
                trays_to_update = location.tray_type_id.id != new_tray_type_id
            # short-circuit this check if we already know that we have to
            # update trays
            if not trays_to_update and "cell_name_format" in vals:
                new_format = vals.get("cell_name_format")
                trays_to_update = location.cell_name_format != new_format
            super(StockLocation, location).write(vals)
            if trays_to_update:
                self._update_tray_sublocations()
            elif "posz" in vals and location.tray_type_id:
                # On initial generation (when tray_to_update is true),
                # the sublocations are already generated with the pos z.
                location.child_ids.write({"posz": vals["posz"]})
        return True

    @api.constrains("active")
    def _tray_check_active(self):
        for record in self:
            if record.active:
                continue
            # We cannot disable any cell of a tray (entire tray)
            # if at least one of the cell contains stock.
            # We cannot disable a tray, a shuffle or a view if
            # at least one of their tray contain stock.
            if record.cell_in_tray_type_id:
                parent = record.location_id
            else:
                parent = record
            # Add the record to the search: as it has been set inactive, it
            # will not be found by the search.
            locs = self.search([("id", "child_of", parent.id)]) | record
            if any(
                (loc.tray_type_id or loc.cell_in_tray_type_id)
                and loc.tray_cell_contains_stock
                for loc in locs
            ):
                raise exceptions.ValidationError(
                    _(
                        "Tray locations cannot be archived when "
                        "they contain products."
                    )
                )

    def _tray_cell_coords(self):
        if not self.cell_in_tray_type_id:
            return []
        return [self.posx - 1, self.posy - 1]

    def _tray_cell_matrix(self):
        assert self.tray_type_id or self.cell_in_tray_type_id
        if self.tray_type_id:
            location = self
        else:  # cell
            location = self.location_id
        cells = location.tray_type_id._generate_cells_matrix()
        for cell in location.child_ids:
            if cell.tray_cell_contains_stock:
                # 1 means used
                cells[cell.posy - 1][cell.posx - 1] = 1
        return cells

    def _format_tray_sublocation_name(self, x, y, z):
        template = self.cell_name_format or self._default_cell_name_format()
        # using format_map allows to have missing replacement strings
        return template.format_map(defaultdict(str, x=x, y=y, z=z))

    @api.multi
    def _update_tray_sublocations(self):
        values = []
        for location in self:
            tray_type = location.tray_type_id

            try:
                location.child_ids.write({"active": False})
            except exceptions.ValidationError:
                # trap this check (_tray_check_active) to display a
                # contextual error message
                raise exceptions.UserError(
                    _(
                        "Trays cannot be modified when "
                        "they contain products."
                    )
                )

            if not tray_type:
                continue

            # create accepts several records now
            posz = location.posz or 0
            for row in range(1, tray_type.rows + 1):
                for col in range(1, tray_type.cols + 1):
                    cell_name = location._format_tray_sublocation_name(
                        col, row, posz
                    )
                    subloc_values = {
                        "name": cell_name,
                        "posx": col,
                        "posy": row,
                        "posz": posz,
                        "location_id": location.id,
                        "company_id": location.company_id.id,
                    }
                    values.append(subloc_values)
        if values:
            self.create(values)

    @api.multi
    def _create_tray_xmlids(self, module):
        """Create external IDs for generated cells

        If the tray location has one. Used for the demo/test data. It will not
        handle properly changing the tray format as the former cells will keep
        the original xmlid built on x and y, the new ones will not be able to
        use them. As these xmlids are meant for the demo data and the tests,
        it is not a problem and should not be used for other purposes.

        Called from stock_location_tray/demo/stock_location_demo.xml.
        """
        for location in self:
            if not location.cell_in_tray_type_id:
                continue
            tray = location.location_id
            tray_external_id = tray.get_external_id().get(tray.id)
            if not tray_external_id:
                continue
            if "." not in tray_external_id:
                continue
            namespace, tray_name = tray_external_id.split(".")
            if module != namespace:
                continue
            tray_external = self.env["ir.model.data"].browse(
                self.env["ir.model.data"]._get_id(module, tray_name)
            )
            cell_external_id = "{}_x{}y{}".format(
                tray_name, location.posx, location.posy
            )
            cell_xmlid = "{}.{}".format(module, cell_external_id)
            if not self.env.ref(cell_xmlid, raise_if_not_found=False):
                self.env["ir.model.data"].create(
                    {
                        "name": cell_external_id,
                        "module": module,
                        "model": self._name,
                        "res_id": location.id,
                        "noupdate": tray_external.noupdate,
                    }
                )
