import json

from odoo import _, api, models


class ReportMrpBomFlat(models.AbstractModel):
    _name = "report.oak_mrp_bom_detail.report_bom_flat"
    _description = _("BOM Single Level Report")

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        for bom_id in docids:
            bom = self.env["mrp.bom"].browse(bom_id)
            variant = data.get("variant")
            candidates = (
                variant
                and self.env["product.product"].browse(variant)
                or bom.product_id
                or bom.product_tmpl_id.product_variant_ids
            )
            quantity = float(data.get("quantity", 1))
            for product_variant_id in candidates.ids:
                if data and data.get("childs"):
                    doc = self._get_pdf_line(
                        bom_id,
                        product_id=product_variant_id,
                        qty=quantity,
                        unfolded_ids=json.loads(data.get("childs")),
                    )
                else:
                    doc = self._get_pdf_line(
                        bom_id,
                        product_id=product_variant_id,
                        qty=quantity,
                        unfolded=True,
                    )
                doc["report_type"] = "pdf"
                doc["report_data"] = data
                docs.append(doc)

            if not candidates:
                if data and data.get("childs"):
                    doc = self._get_pdf_line(
                        bom_id,
                        qty=quantity,
                        unfolded_ids=json.loads(data.get("childs")),
                    )
                else:
                    doc = self._get_pdf_line(bom_id, qty=quantity, unfolded=True)
                doc["report_type"] = "pdf"
                doc["report_data"] = data
                docs.append(doc)
        return {"doc_ids": docids, "doc_model": "mrp.bom", "docs": docs}

    @api.model
    def get_bom(
        self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False
    ):
        lines = self._get_bom(
            bom_id=bom_id,
            product_id=product_id,
            line_qty=line_qty,
            line_id=line_id,
            level=level,
        )
        return self.env.ref("mrp.report_mrp_bom_line")._render({"data": lines})

    @api.model
    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
        lines = {}
        bom = self.env["mrp.bom"].browse(bom_id)
        bom_quantity = searchQty or bom.product_qty or 1
        bom_product_variants = {}
        bom_uom_name = ""

        if bom:
            bom_uom_name = bom.product_uom_id.name

            # Get variants used for search
            if not bom.product_id:
                for variant in bom.product_tmpl_id.product_variant_ids:
                    bom_product_variants[variant.id] = variant.display_name

        lines = self._get_bom(
            bom_id, product_id=searchVariant, line_qty=bom_quantity, level=1
        )
        return {
            "lines": lines,
            "variants": bom_product_variants,
            "bom_uom_name": bom_uom_name,
            "bom_qty": bom_quantity,
            "is_variant_applied": self.env.user.user_has_groups(
                "product.group_product_variant"
            )
            and len(bom_product_variants) > 1,
            "is_uom_applied": self.env.user.user_has_groups("uom.group_uom"),
        }

    def _get_bom(
        self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False
    ):
        bom = self.env["mrp.bom"].browse(bom_id)
        company = self.env.company
        bom_quantity = line_qty
        if line_id:
            current_line = self.env["mrp.bom.line"].browse(int(line_id))
            bom_quantity = (
                current_line.product_uom_id._compute_quantity(
                    line_qty, bom.product_uom_id
                )
                or 0
            )
        # Display bom components for current selected product variant
        if product_id:
            product = self.env["product.product"].browse(int(product_id))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        bom_quantity = float(bom_quantity)
        lines = {
            "bom": bom,
            "bom_qty": bom_quantity,
            "det_name": product.product_tmpl_id.detail_number_id.name,
            "default_code": product.default_code,
            "product_name": product.product_tmpl_id.name,
            "bom_prod_name": product.display_name,
            "product": product,
            "company": company,
            "code": bom and bom.display_name or "",
            "level": level or 0,
        }
        components = self._get_bom_lines(bom, bom_quantity, product, line_id, level)
        lines["components"] = components
        return lines

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            line_quantity = float(line_quantity)
            if line._skip_bom_line(product):
                continue
            company = self.env.company
            components.append(
                {
                    "prod_id": line.product_id.id,
                    "det_name": line.product_id.product_tmpl_id.detail_number_id.name,
                    "default_code": line.product_id.default_code,
                    "prod_name": line.product_id.product_tmpl_id.name,
                    "code": line.child_bom_id and line.child_bom_id.display_name or "",
                    "prod_qty": line_quantity,
                    "prod_uom": line.product_uom_id.name,
                    "parent_id": bom.id,
                    "line_id": line.id,
                    "level": level or 0,
                    "company": company,
                    "child_bom": line.child_bom_id.id,
                    "phantom_bom": line.child_bom_id
                    and line.child_bom_id.type == "phantom"
                    or False,
                }
            )
        return components

    def _get_pdf_line(self, bom_id, product_id, qty, unfolded=False):
        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(
                bom_id=bom.id,
                product_id=product_id,
                line_qty=line_qty,
                line_id=line_id,
                level=level,
            )
            bom_lines = data["components"]
            lines = []
            for bom_line in bom_lines:

                lines.append(
                    {
                        "name": bom_line["prod_name"],
                        "type": "bom",
                        "det_name": bom_line["det_name"],
                        "default_code": bom_line["default_code"],
                        "quantity": bom_line["prod_qty"],
                        "uom": bom_line["prod_uom"],
                        "level": bom_line["level"],
                        "code": bom_line["code"],
                        "company": bom_line["company"],
                        "child_bom": bom_line["child_bom"],
                        "prod_id": bom_line["prod_id"],
                    }
                )
            return lines

        bom = self.env["mrp.bom"].browse(bom_id)
        product_id = (
            product_id or bom.product_id.id or bom.product_tmpl_id.product_variant_id.id
        )
        data = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=qty)
        pdf_lines = get_sub_lines(bom, product_id, qty, False, 1)
        data["components"] = []
        data["lines"] = pdf_lines
        return data
