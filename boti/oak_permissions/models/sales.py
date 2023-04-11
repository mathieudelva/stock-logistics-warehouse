from odoo import api, models


# Inheriting the sale.order modifying exiting group access
class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def move_cwu_group_access(self, from_group_name, to_group_name):
        # move non-read of renamed readonly access to custom view all edit own
        category_domain = [("name", "=", "Sales")]
        sale_category_ids = self.env["ir.module.category"].search(
            category_domain, limit=1
        )
        for sale_category_id in sale_category_ids:
            from_group_domain = [
                "&",
                ("name", "=", from_group_name),
                ("category_id", "=", sale_category_id.id),
            ]
            to_group_domain = [
                "&",
                ("name", "=", to_group_name),
                ("category_id", "=", sale_category_id.id),
            ]
        from_group = self.env["res.groups"].search(from_group_domain, limit=1)
        to_group = self.env["res.groups"].search(to_group_domain, limit=1)
        access_update_domain = [("group_id", "=", from_group.id)]
        access_lines = self.env["ir.model.access"].search(access_update_domain)
        for access in access_lines:
            rec = self.env["ir.model.access"].browse(access.id)
            if (
                rec.perm_write is True
                or rec.perm_create is True
                or rec.perm_unlink is True
            ):
                vals = {}
                vals["group_id"] = to_group.id
                rec.write(vals)
