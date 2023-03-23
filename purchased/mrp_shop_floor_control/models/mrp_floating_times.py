from pytz import utc

from odoo import _, api, fields, models
from odoo.exceptions import UserError


def make_aware(dt):
    """Return ``dt`` with an explicit timezone, together with a function to
    convert a datetime to the same (naive or aware) timezone as ``dt``.
    """
    if dt.tzinfo:
        return dt, lambda val: val.astimezone(dt.tzinfo)
    else:
        return dt.replace(tzinfo=utc), lambda val: val.astimezone(utc).replace(
            tzinfo=None
        )


class MrpFloatingTimes(models.Model):
    _name = "mrp.floating.times"
    _description = "MRP Floating Times"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        "Warehouse",
        required=True,
        domain="[('manufacture_to_resupply', '=', 'True')]",
    )
    company_id = fields.Many2one(
        "res.company", "Company", related="warehouse_id.company_id", readonly=True
    )
    mrp_release_time = fields.Float("Release Time (Hours)", default=1.0)
    mrp_ftbp_time = fields.Float("Floating Time Before Production (Hours)", default=1.0)
    mrp_ftap_time = fields.Float("Floating Time After Production (Hours)", default=1.0)

    @api.constrains("warehouse_id")
    def _check_same_warehouse(self):
        for record in self:
            ft_ids = self.env["mrp.floating.times"].search(
                [("warehouse_id", "=", record.warehouse_id.id)]
            )
            if len(ft_ids) > 1:
                raise UserError(
                    _("Another Floating Times record exists in the same warehouse: %s")
                    % record.warehouse_id.name
                )

    def create_floating_times(self):
        warehouses = (
            self.env["stock.warehouse"]
            .with_context(active_test=False)
            .search([("manufacture_to_resupply", "=", True)])
        )
        for warehouse in warehouses:
            self.create(
                {
                    "warehouse_id": warehouse.id,
                    "mrp_release_time": 1.0,
                    "mrp_ftbp_time": 1.0,
                    "mrp_ftap_time": 1.0,
                }
            )
