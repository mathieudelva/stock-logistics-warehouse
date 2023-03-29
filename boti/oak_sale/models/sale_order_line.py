from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    promise_date = fields.Datetime(index=True)

    def write(self, vals):
        for rec in self:
            old_date = rec.promise_date
        res = super(SaleOrderLine, self).write(vals)
        # Keep track of promise date
        if "promise_date" in vals:
            new_date = vals["promise_date"]
            self.order_id.message_post(
                body=_(
                    "Promise Date <br> %(olddate)s -> %(newdate)s",
                    olddate=old_date,
                    newdate=new_date,
                ),
            )
        return res

    @api.model_create_multi
    def create(self, vals):
        # if no promise date use commitment
        for val in vals:
            if "promise_date" in val:
                if val["promise_date"] is False:
                    if "commitment_date" in val:
                        val["promise_date"] = val["commitment_date"]
            # need an else for planned orders where requested does not exist
            else:
                if "commitment_date" in val:
                    val["requested_date"] = val["commitment_date"]
        res = super(SaleOrderLine, self).create(vals)
        return res
