import logging

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


# Combined view of imported Active plus
class ProductCombine(models.Model):
    _name = "product.combine"
    _description = "Active plus Legacy Products view"
    _check_company_auto = True
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _auto = False
    _order = "create_date"

    def _get_default_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order="id").id

    product_tmpl_id = fields.Integer()

    product_legacy_id = fields.Integer()

    default_code = fields.Char(string="Product ID")

    name = fields.Char(string="Description")

    detail_number_id = fields.Many2one(
        "product.detail.number", "Detail Number", help="Product Detail Numbers"
    )

    generic_name_id = fields.Many2one(
        "product.generic.name", "Generic name", help="Product Generic Names"
    )

    product_status = fields.Selection(
        [("Active", "Odoo Product"), ("Legacy", "Legacy Product")],
        string="Status",
        default="Active",
        required=True,
        help="Status of product in this list Odoo Product or old Legacy Product",
    )

    finish_size = fields.Char(string="Finished size")

    eng_note = fields.Text(string="Engineering notes")

    description = fields.Text(string="Internal Notes")

    message_main_attachment_id = fields.Integer()

    write_id = fields.Integer()

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
    material_name = fields.Char(
        string="Material Name", related="material_id.name", readonly=True
    )

    class_id = fields.Many2one(
        "product.class", "Class", help="Product Engineer Classification"
    )
    class_name = fields.Char(
        string="Class Name", related="class_id.name", readonly=True
    )

    bom_count = fields.Integer(
        "# Bill of Material", compute="_compute_bom_count", compute_sudo=False
    )

    bom_count_legacy = fields.Integer(
        "# Legacy BoM", compute="_compute_bom_count_legacy", compute_sudo=False
    )

    routing_count = fields.Integer(
        "# Routings", compute="_compute_routing_count", compute_sudo=False
    )

    active_product_id = fields.Integer(
        "Product Rec Id", compute="_compute_product_id", compute_sudo=False
    )

    legacy_bomid = fields.Char(compute="_compute_legacy_bomid", compute_sudo=True)

    active = fields.Boolean()

    cnc_info_line = fields.One2many(
        comodel_name="product.legacy.cnc.line",
        inverse_name="product_legacy_id",
        string="Legacy CNC Program Info",
        copy=False,
        readonly=True,
    )

    def info(self, title, message):
        view = self.env.ref("oak_legacy.message_box")
        context = dict(self.env.context or {})
        context["message"] = message
        return {
            "name": title,
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "message.box",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": context,
        }

    def open_product_form(self):
        for record in self:
            if record.product_status == "Variant":
                product = self.env["product.product"].search(
                    [("default_code", "=", record.default_code)]
                )
                return {
                    "name": ("Product Form"),
                    "domain": [("id", "in", product.ids)],
                    "view_type": "form",
                    "res_model": "product.product",
                    "res_id": product.id,
                    "view_id": False,
                    "view_mode": "form",
                    "type": "ir.actions.act_window",
                }
            else:
                product_tmpl = self.env["product.template"].search(
                    [("default_code", "=", record.default_code)]
                )
                return {
                    "name": ("Product Form"),
                    "domain": [("id", "in", product_tmpl.ids)],
                    "view_type": "form",
                    "res_model": "product.template",
                    "res_id": product_tmpl.id,
                    "view_id": False,
                    "view_mode": "form",
                    "type": "ir.actions.act_window",
                }

    def open_new_product_form(self):
        for record in self:
            return {
                "name": ("New Draft Product Form"),
                "domain": [],
                "view_type": "form",
                "res_model": "product.template",
                "view_id": record.env.ref(
                    "oak_product.product_template_form_oak_view"
                ).id,
                "view_mode": "form",
                "type": "ir.actions.act_window",
            }

    def import_bom_single(self):
        code = self.default_code
        result = self._convert_legacy_bom_recurse(code, False)
        if not result[1]:
            return {"type": "ir.actions.client", "tag": "reload"}
        else:
            return self.info("Conversion Errors!", result[1])

    def import_bom(self):
        code = self.default_code
        result = self._convert_legacy_bom_recurse(code)
        if not result[1]:
            return {"type": "ir.actions.client", "tag": "reload"}
        else:
            return self.info("Conversion Errors!", result[1])

    def _create_or_verify_product(self):
        for record in self:
            code = record.default_code
            lproduct = self.env["product.product"].search([("default_code", "=", code)])
            lproduct_tmpl = self.env["product.template"].search(
                [("default_code", "=", code)]
            )

            if not lproduct_tmpl.id:
                # convert the legacy product to odoo
                try:
                    legacy_item_record = self.env["product.combine"].search(
                        [("default_code", "=", code)]
                    )
                    legacy_found = True
                except Exception as e:
                    _logger.warning(
                        "Error product.combine _create_or_verify_product: %s", e
                    )
                    return False, False, False

                if legacy_found:
                    search_code = legacy_item_record.default_code
                    legacy_item_record.convert_to_draft()
                    lproduct = self.env["product.product"].search(
                        [("default_code", "=", search_code)]
                    )
                    lproduct_tmpl = self.env["product.template"].search(
                        [("default_code", "=", search_code)]
                    )
                else:
                    # no odoo product no legacy product were found
                    lproduct_tmpl = lproduct = False

            return lproduct_tmpl, lproduct, True

    def _valid_legacy_bom_position(self, legacybomline):
        posit = 10
        if str(legacybomline.position).isnumeric():
            posit = int(legacybomline.position)
        return posit

    def _convert_legacy_uom(self, legacybomline):
        lunit = legacybomline.unitid

        # default uomrec if not found in unit_conversion_dict]
        uomrec = self.env["product.legacy.uom"].search([("legacy_uom", "=", lunit)])
        return uomrec.odoo_uom.id

    def _convert_legacy_bom_recurse(self, default_code, recurse=True):
        """This routine is now a conversion from legacy tables to standard bom tables"""
        retVal = False
        retMsg = ""
        # now read legacy data and convert
        product_tmpl = self.env["product.template"].search(
            [("default_code", "=", default_code)]
        )
        legacy_bom_record = self.env["mrp.bom.legacy"].search(
            [("name", "=", default_code)], limit=1
        )

        bval = {}
        bval["active"] = True
        if legacy_bom_record.bomtype == "1":
            bval["type"] = "phantom"
        else:
            bval["type"] = "normal"

        bval["product_tmpl_id"] = product_tmpl.id
        # val['product_id']=product.id
        bval["product_qty"] = 1
        bval["product_uom_id"] = product_tmpl.uom_id.id
        bval["ready_to_produce"] = "asap"
        bval["consumption"] = "strict"

        # check to see if odoo BoM already exists if not add it
        obom = self.env["mrp.bom"].search([("product_tmpl_id", "=", product_tmpl.id)])
        # note only traverse the BoM if the Odoo BoM does not exist
        if not obom.id:
            obom = self.env["mrp.bom"].create(bval)
            if obom.id:
                # create an external id
                self.create_verify_external_id(
                    "__migrate__", "mrp_bom_" + default_code, "mrp.bom", obom.id
                )
            retVal = True
            mrp_bom_line_legacy = self.env["mrp.bom.line.legacy"]
            legacybomlines = mrp_bom_line_legacy.search(
                [("bom_id", "=", legacy_bom_record.id)]
            )

            for legacybomline in legacybomlines:
                if legacybomline.itemid:
                    search_code = legacybomline.itemid
                    item_rec = self.env["product.combine"].search(
                        [("default_code", "=", search_code)]
                    )
                    recs = item_rec._create_or_verify_product()
                    if recs[2]:
                        lproduct_tmpl = recs[0]
                        lproduct = recs[1]

                        if lproduct_tmpl.id and lproduct.id:
                            lval = {}
                            lval["product_id"] = lproduct.id
                            lval["product_tmpl_id"] = lproduct_tmpl.id
                            lval["product_qty"] = legacybomline.bomqty
                            lval["bom_id"] = obom.id
                            posit = item_rec._valid_legacy_bom_position(legacybomline)
                            lval["sequence"] = posit
                            lval["product_uom_id"] = item_rec._convert_legacy_uom(
                                legacybomline
                            )
                            lval["external_ref"] = legacybomline.external_ref

                            exists_mrpbomline = self.env["mrp.bom.line"].search(
                                [
                                    ("product_id", "=", lproduct.id),
                                    ("bom_id", "=", obom.id),
                                    ("sequence", "=", posit),
                                ]
                            )
                            if not exists_mrpbomline.ids:
                                # add bom line
                                mrpbomline = self.env["mrp.bom.line"].create(lval)
                                # create external id
                                if mrpbomline.id:
                                    self.create_verify_external_id(
                                        "__migrate__",
                                        "mrp_bom_line_%s_%s"
                                        % (default_code, search_code),
                                        "mrp.bom.line",
                                        mrpbomline.id,
                                    )
                            else:
                                mrpbomline = exists_mrpbomline

                            bomcnt = 0
                            check_lproduct_tmpl = mrpbomline.product_tmpl_id
                            lbomcnt = check_lproduct_tmpl.get_legacy_bom_count()

                            # recurse if the bomline has a legacy bom and recurse is true
                            if bomcnt == 0 and lbomcnt > 0 and recurse:
                                code = lproduct.default_code
                                result = self._convert_legacy_bom_recurse(code)
                                retMsg += result[1]

                        else:
                            bomcnt = 0
                            lbomcnt = 0
                            _logger.warning("Item not found: %s", legacybomline.itemid)
                            retMsg += (
                                "BoM Product not found:" + legacybomline.itemid + ", "
                            )

        # True BoM(s) are imported, False nothing done
        return retVal, retMsg

    def view_bom(self):
        action = self.env.ref("mrp.product_open_bom").sudo().read()[0]
        for record in self:
            product_tmpl = self.env["product.template"].search(
                [("default_code", "=", record.default_code)]
            )
            product = self.env["product.product"].search(
                [("default_code", "=", record.default_code)]
            )

            # bom specific to this variant or global to template
            action["context"] = {
                "default_product_tmpl_id": product_tmpl.id,
                "default_product_id": product.id,
            }
            action["domain"] = [
                "|",
                ("product_id", "in", product.ids),
                "&",
                ("product_id", "=", False),
                ("product_tmpl_id", "in", product_tmpl.ids),
            ]
            return action

    def _compute_bom_count(self):
        for record in self:
            if record.product_status == "Active":
                product = self.env["product.template"].search(
                    [("default_code", "=", record.default_code)]
                )
                record.bom_count = self.env["mrp.bom"].search_count(
                    [("product_tmpl_id", "=", product.id)]
                )
            elif record.product_status == "Variant":
                product = self.env["product.product"].search(
                    [("default_code", "=", record.default_code)]
                )
                record.bom_count = self.env["mrp.bom"].search_count(
                    [("product_id", "=", product.id)]
                )
            else:
                record.bom_count = 0

    def view_legacy_bom(self):
        for record in self:
            if record.bom_count_legacy > 0:
                # get legacy bom record
                bomrec = self.env["mrp.bom.legacy"].search(
                    [("name", "=", record.default_code)]
                )

                return {
                    "name": ("View Legacy BoM"),
                    "domain": [("id", "in", bomrec.ids)],
                    "view_type": "form",
                    "res_model": "mrp.bom.legacy",
                    "res_id": bomrec.id,
                    "view_id": False,
                    "view_mode": "form",
                    "type": "ir.actions.act_window",
                }
            else:
                return False

    def view_legacy_routing(self):
        for record in self:
            if record.routing_count > 0:
                # get legacy bom record
                routingrec = self.env["mrp.routing.legacy"].search(
                    [("itemid", "=", record.default_code)]
                )

                return {
                    "name": ("View Legacy Routings"),
                    "domain": [("id", "in", routingrec.ids)],
                    "res_model": "mrp.routing.legacy",
                    "view_id": False,
                    "view_mode": "tree,form",
                    "type": "ir.actions.act_window",
                }
            else:
                return False

    def get_legacy_bom_count(self):
        for record in self:
            return self.env["mrp.bom.legacy"].search_count(
                [("name", "=", record.default_code)]
            )

    def _compute_bom_count_legacy(self):
        for record in self:
            record.bom_count_legacy = self.env["mrp.bom.legacy"].search_count(
                [("name", "=", record.default_code)]
            )

    def _compute_routing_count(self):
        for record in self:
            record.routing_count = self.env["mrp.routing.legacy"].search_count(
                [("itemid", "=", record.default_code)]
            )

    def _get_sql_query(self):
        return """
CREATE VIEW public.product_combine
 AS
 SELECT pt.id,
    pt.id AS product_tmpl_id,
    0 AS product_legacy_id,
    pt.default_code,
    pt.detail_number_id,
    pt.generic_name_id,
    pt.class_id,
    pt.name->>'en_US' as name,
    'Active'::text AS product_status,
    pt.type,
    pt.description->>'en_US' as description,
    pt.finish_size,
    pt.eng_note,
    pt.uom_id,
    pt.uom_po_id,
    pt.id AS write_id,
    pt.message_main_attachment_id,
    pt.create_date,
    pt.create_uid,
    pt.write_date,
    pt.write_uid,
    pt.material_id,
    pt.active
   FROM product_template pt
UNION ALL
 SELECT pl.id + 500000 AS id,
    0 AS product_tmpl_id,
    pl.id AS product_legacy_id,
    pl.default_code,
    pl.detail_number_id,
    pl.generic_name_id,
    pl.class_id,
    pl.name,
    'Legacy'::text AS product_status,
    pl.type,
    pl.description,
    pl.finish_size,
    pl.eng_note,
    pl.uom_id,
    pl.uom_po_id,
    pl.id AS write_id,
    0 AS message_main_attachment_id,
    pl.create_date,
    pl.create_uid,
    pl.write_date,
    pl.write_uid,
    pl.material_id,
        CASE
            WHEN p_t.active IS NULL THEN true
            ELSE false
        END AS active
   FROM product_legacy pl
     LEFT JOIN product_template p_t ON pl.default_code::text = p_t.default_code::text;
            """

    def init(self):
        tools.drop_view_if_exists(self._cr, "product_combine")
        query = self._get_sql_query()
        self._cr.execute(query)

    def button_convert_to_draft(self):
        for record in self:
            save_code = record.default_code
        result = self.convert_to_draft()
        if result[1] == "Success!":
            active_rec = self.env["product.template"].search(
                [("default_code", "=", save_code)]
            )
            if active_rec.id:
                product_comb = self.env["product.combine"].search(
                    [("default_code", "=", save_code)]
                )
                return {
                    "name": ("Product Form"),
                    "domain": [("id", "in", product_comb.ids)],
                    "view_type": "form",
                    "res_model": "product.combine",
                    "res_id": product_comb.id,
                    "view_id": record.env.ref(
                        "oak_legacy.product_combine_form_view"
                    ).id,
                    "view_mode": "form",
                    "type": "ir.actions.act_window",
                }
        else:
            return self.info(result[1], result[2])

    def convert_to_draft(self):
        for record in self:
            if record.product_status == "Legacy":
                default_code = record.default_code
                _logger.info("Convert Legacy to Draft: %s, %s", default_code, self.name)
                # create the new product
                val = {}
                val["default_code"] = default_code
                val["barcode"] = default_code
                val["type"] = record.type
                val["detail_number_id"] = record.detail_number_id.id
                val["generic_name_id"] = record.generic_name_id.id
                val["name"] = record.name
                val["description"] = record.description
                val["class_id"] = record.class_id.id
                val["uom_id"] = record.uom_id.id
                val["uom_po_id"] = record.uom_po_id.id
                val["categ_id"] = (
                    self.env["product.category"].search([("name", "=", "Draft")]).id
                )
                record = self.env["product.template"].create(val)
                if record.id > 0:
                    # create an external id
                    self.create_verify_external_id(
                        "from_ax",
                        "product_template_" + record.default_code,
                        "product.template",
                        record.id,
                    )
                    # success
                    ret_result = "Success!"
                    msg = default_code + " converted to Odoo Draft product."
                else:
                    ret_result = "Something went wrong!"
                    msg = default_code + " conversion failed."
        return record, ret_result, msg

    def write(self, vals):

        # if Legacy product write it
        if self.product_status == "Legacy":
            self.ensure_one()
            write_legacy_fields = [
                "name",
                "description",
                "type",
                "detail_number_id",
                "generic_name",
                "eng_note",
                "finish_size",
                "material_id",
                "class_id",
                "uom_id",
                "uom_po_id",
                "legacy_write_date",
                "legacy_create_date",
            ]
            val = {}

            legacy_record = self.env["product.legacy"].search(
                [("default_code", "=", self.default_code)]
            )  # get legacy record

            for key, value in vals.items():
                if key in write_legacy_fields:
                    val[key] = value

            if len(val) > 0:
                legacy_record.write(val)  # update legacy record

        # if Active product write it
        if self.product_status == "Active":
            self.ensure_one()
            write_active_fields = [
                "name",
                "description",
                "type",
                "detail_number_id",
                "generic_name",
                "eng_note",
                "finish_size",
                "material_id",
                "class_id",
                "uom_id",
                "uom_po_id",
            ]
            val2 = {}

            active_record = self.env["product.template"].search(
                [("default_code", "=", self.default_code)]
            )  # get active record

            for key, value in vals.items():
                if key in write_active_fields:
                    val2[key] = value

            if len(val2) > 0:
                active_record.write(val2)  # update active record

        return super().write({})

    def unlink(self):
        return super(
            self.info(self, "Not Allowed!", "Delete is not allowed in this module.")
        )

    def create_verify_external_id(
        self, prefix_identifier, unique_identifier, modelname, new_rec_id
    ):
        external_identifier = unique_identifier

        try:
            external_id = self.env["ir.model.data"]._xmlid_lookup(
                prefix_identifier + "." + external_identifier
            )
        except ValueError:
            external_id = False

        # check for external id
        if not external_id:
            # Create the external ID
            self.env["ir.model.data"].create(
                {
                    "module": prefix_identifier,
                    "name": external_identifier,
                    "model": modelname,
                    "res_id": new_rec_id,
                }
            )
        return True
