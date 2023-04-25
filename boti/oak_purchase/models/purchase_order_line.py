from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    requested_date = fields.Datetime(string="Requested Receipt Date", index=True)

    def write(self, vals):
        old_date = None
        for rec in self:
            old_date = rec.requested_date
        res = super(PurchaseOrderLine, self).write(vals)
        # Keep track of requested date change
        if "requested_date" in vals:
            new_date = vals["requested_date"]
            self.order_id.message_post(
                body=_(
                    "Requested Date Changed <br> %(olddate)s -> %(newdate)s",
                    olddate=old_date,
                    newdate=new_date,
                )
            )
        return res

    @api.model_create_multi
    def create(self, vals):
        # if no requested date use planned
        for val in vals:
            if "requested_date" in val:
                if val["requested_date"] is False:
                    if "date_planned" in val:
                        val["requested_date"] = val["date_planned"]
            # need an else for planned orders where requested does not exist
            else:
                if "date_planned" in val:
                    val["requested_date"] = val["date_planned"]
        res = super(PurchaseOrderLine, self).create(vals)
        return res
