from odoo import fields, models, tools


# Imported product not added to master but available to import
class ProductLegacy(models.Model):
    _name = "product.legacy"
    _description = "Legacy Products"
    _check_company_auto = True
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_default_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order="id").id

    default_code = fields.Char(string="Product Number", required="True")

    name = fields.Char(string="Description")

    detail_number_id = fields.Many2one(
        "product.detail.number", "Detail Number", help="Product Detail Numbers"
    )

    generic_name_id = fields.Many2one(
        "product.generic.name", "Generic name", help="Product Generic Name"
    )

    product_status = fields.Selection(
        [("Active", "Odoo Product"), ("Legacy", "Legacy Product")],
        string="Status",
        default="Legacy",
        required=True,
        help="Status of product in this list Odoo Product or old Legacy Product",
    )

    finish_size = fields.Char(string="Finished size")

    description = fields.Text(string="Internal Notes")

    eng_note = fields.Text(string="Engineering notes")

    externaldb_reference = fields.Char(string="External DB Reference")

    message_main_attachment_id = fields.Integer()

    type = fields.Selection(
        [
            ("product", "Storable Product"),
            ("consu", "Consumable"),
            ("service", "Service"),
        ],
        string="Product Type",
        default="product",
        required=True,
        help="Product Types, Storable Product, Consumable, Service",
    )

    create_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)

    write_date = fields.Datetime(string="Modified Date", default=fields.Datetime.now)

    uom_id = fields.Many2one(
        "uom.uom",
        "Unit of Measure",
        default=_get_default_uom_id,
        required=True,
        help="Default unit of measure used for all stock operations.",
    )

    uom_name = fields.Char(
        string="Unit of Measure Name", related="uom_id.name", readonly=True
    )
    uom_po_id = fields.Many2one(
        "uom.uom",
        "Purchase Unit of Measure",
        default=_get_default_uom_id,
        required=True,
        help="Default UOM for purchase orders. Must be same category as default UOM.",
    )

    material_id = fields.Many2one(
        "product.material", "Material", help="Product material"
    )

    class_id = fields.Many2one(
        "product.class", "Class", help="Product Engineer Classification"
    )

    list_price_legacy = fields.Float(string="Legacy List Price")
    std_cost_legacy = fields.Float(string="Legacy Std Cost")

    def init(self):
        tools.create_index(
            self._cr, "product_legacy_active_index", self._table, ["default_code"]
        )
