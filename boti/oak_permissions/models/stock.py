from odoo import api, models


# Inheriting stock_inventory api and model
class Inventory(models.Model):
    _inherit = "stock.quant"

    @api.model
    def move_cwu_group_access(self, from_group, to_group):
        # move write create unlink accesses
        category_domain = [("name", "=", "Inventory")]
        stock_category_ids = self.env["ir.module.category"].search(
            category_domain, limit=1
        )
        for stock_category_id in stock_category_ids:
            from_group_domain = [
                "&",
                ("name", "=", from_group),
                ("category_id", "=", stock_category_id.id),
            ]
            to_group_domain = [
                "&",
                ("name", "=", to_group),
                ("category_id", "=", stock_category_id.id),
            ]
        from_group_ids = self.env["res.groups"].search(from_group_domain, limit=1)
        access_ids = {}
        if from_group_ids:
            from_group_id = from_group_ids[0].id
            access_update_domain = [("group_id", "=", from_group_id)]
            access_ids = self.env["ir.model.access"].search(access_update_domain)
        to_group_ids = self.env["res.groups"].search(to_group_domain, limit=1)
        if to_group_ids:
            to_group_id = to_group_ids[0].id

        for access_id in access_ids:
            rec = self.env["ir.model.access"].browse(access_id.id)
            if (
                rec.perm_write is True
                or rec.perm_create is True
                or rec.perm_unlink is True
            ):
                vals = {}
                vals["group_id"] = to_group_id
                rec.write(vals)
