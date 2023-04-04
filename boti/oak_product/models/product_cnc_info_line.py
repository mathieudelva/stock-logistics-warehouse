from odoo import api, fields, models


class ProductCNCInfoLine(models.Model):
    _name = "product.cnc.info.line"
    _description = "Product CNC Info"
    _order = "name"
    _check_company_auto = True

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )

    sequence = fields.Integer(default=10)

    name = fields.Char(string="Program")
    cnc_length = fields.Float(string="CNC - Length")
    cnc_diameter = fields.Float(string="CNC - Diameter")
    workcenter_id = fields.Many2one("mrp.workcenter", "Work Center")
    department_id = fields.Char(
        readonly=True, string="Department", compute="_compute_department_id"
    )

    # Related field on department id caused circular dependency
    # The purpose of this is to prevent that
    @api.depends("workcenter_id")
    def _compute_department_id(self):
        for record in self:
            if "department_id" in self.env["mrp.workcenter"]._fields:
                record.department_id = record.workcenter_id.department_id.name
            else:
                record.department_id = "None"
