from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_warranty_policy_sales = fields.Boolean("Warranty Disclaimer")

    @api.model
    def set_values(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "sale.use_warranty_policy_sales", self.use_warranty_policy_sales
        )

        return super(ResConfigSettings, self).set_values()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res["use_warranty_policy_sales"] = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.use_warranty_policy_sales", default=False)
        )

        return res
