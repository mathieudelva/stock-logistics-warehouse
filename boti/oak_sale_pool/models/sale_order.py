from odoo import fields, models


# Sales Type (pool) enhancement
class SaleOrder(models.Model):
    _inherit = "sale.order"

    sales_pool_id = fields.Many2one(
        "account.analytic.plan", "Sales Type", help="Sales Type (Pool)"
    )
    custom_aa_name = fields.Char("Custom AA Name")
    use_custom_name = fields.Boolean(related="sales_pool_id.use_custom_name")

    analytic_plan_id = fields.Many2one(
        related="analytic_account_id.plan_id", store=True
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_line_analytic_plan_id = fields.Many2one(
        "account.analytic.plan", "Sales Type", help="Sales Type (Pool)"
    )

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        account_id = 0
        analytic_plan_id = self.sale_line_analytic_plan_id.id
        if analytic_plan_id > 0:
            records = self.env["sale.type.account"].sudo().search([])
            for record in records:
                chk_analytic_plan_id = record.sale_line_analytic_plan_id.id
                if chk_analytic_plan_id == analytic_plan_id:
                    account_id = record.account_id.id
            if account_id > 0:
                res.update(
                    {
                        "sale_line_analytic_plan_id": self.sale_line_analytic_plan_id,
                        "account_id": account_id,
                    }
                )
            else:
                res.update(
                    {"sale_line_analytic_plan_id": self.sale_line_analytic_plan_id}
                )

        return res

    def write(self, values):
        # default to the sales line if not set
        if (
            "sale_line_analytic_plan_id" not in values
            and not self.sale_line_analytic_plan_id
        ):
            values["sale_line_analytic_plan_id"] = self.order_id.sales_pool_id.id

        return super(SaleOrderLine, self).write(values)
