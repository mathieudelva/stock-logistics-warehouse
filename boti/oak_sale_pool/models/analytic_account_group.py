from odoo import fields, models


class AccountAnalyticGroup(models.Model):
    _inherit = "account.analytic.group"

    prefix = fields.Char(trim=False)
    suffix = fields.Char(trim=False)
    use_custom_name = fields.Boolean()


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def name_get(self):
        for analytic in self:
            if analytic.group_id:
                so_id = self.env["sale.order"].search(
                    [("analytic_account_id", "=", analytic.id)], limit=1
                )
                res = []
                if so_id and so_id.custom_aa_name:
                    partner_name = so_id.custom_aa_name
                else:
                    partner_name = analytic.partner_id.commercial_partner_id.name

                if not partner_name:
                    name = analytic.name
                else:
                    name = analytic.name + " - " + partner_name

                if analytic.group_id.prefix:
                    name = analytic.group_id.prefix + name
                if analytic.group_id.suffix:
                    name = name + analytic.group_id.suffix
                res.append((analytic.id, name))
                return res
            else:
                return super().name_get()
