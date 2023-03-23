from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def open_bom(self):
        self.ensure_one()
        if self.child_bom_id:
            return {
                "res_id": self.child_bom_id.id,
                "domain": "[('id','=', " + str(self.child_bom_id.id) + ")]",
                "name": _("BOM"),
                "view_type": "form",
                "view_mode": "form,tree",
                "res_model": "mrp.bom",
                "view_id": False,
                "target": "current",
                "type": "ir.actions.act_window",
            }


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    recursion = fields.Boolean(compute="_get_bom_recursion", store=True)
    tool_ids = fields.One2many("mrp.bom.tool", "bom_id", "Tools")

    @api.depends("bom_line_ids.product_id", "product_tmpl_id", "product_id")
    def _get_bom_recursion(self):
        for bom in self:
            bom.recursion = False
            for line in bom.bom_line_ids:
                if line.product_id in bom.product_tmpl_id.product_variant_ids:
                    bom.recursion = True

    @api.constrains("recursion")
    def _check_bom_recursion(self):
        for bom in self:
            if bom.recursion:
                raise UserError(_("Recursive BoM is not allowed."))


class MrpBoMTools(models.Model):
    _name = "mrp.bom.tool"
    _description = "Production BoM Tools"

    tool_id = fields.Many2one("mrp.tool", "Tool", required=True)
    bom_id = fields.Many2one("mrp.bom", "Bill of Materials")

    @api.constrains("tool_id")
    def check_tool_id(self):
        for record in self:
            for tool in record.bom_id.tool_ids:
                tools = self.search(
                    [
                        ("bom_id", "=", record.bom_id.id),
                        ("tool_id", "=", record.tool_id.id),
                    ]
                )
            if len(tools) > 1:
                raise UserError(_("Tool already entered"))

    ##tool attachment
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [
            "&",
            ("res_model", "=", "mrp.tool"),
            ("res_id", "in", self.tool_id.ids),
        ]
        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "ir.attachment",
            #'views': [(self.env.ref('mrp_shop_floor_control.view_ir_attachment_kanban').id, "kanban")],
            "view_mode": "kanban",
            "view_id": False,
            "type": "ir.actions.act_window",
            "limit": 80,
            "context": "{'default_res_model': '%s','default_res_id': %d, 'create': 0}"
            % (self._name, self.id),
        }
