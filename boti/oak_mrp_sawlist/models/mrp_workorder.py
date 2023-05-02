from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"
    _description = "MRP Workorder"

    finish_size = fields.Char(related="product_id.product_tmpl_id.finish_size")
    material = fields.Char()
    raw_size = fields.Char()
    raw_length = fields.Float("Length")
    ovr_qty = fields.Float("Override Qty")

    def _get_raw_size(self, record):
        ret = ""
        for recid in record.production_id.move_raw_ids:
            strchk = recid.product_id.name
            fieldnum = 2
            # ugly check
            if "Aluminum Bronze" in strchk:
                fieldnum = 1
            size_list = strchk.split(",")
            classcode = recid.product_id.product_tmpl_id.class_id.name
            if (
                len(size_list) > 2
                and classcode == "RAW MATRL"
                and record.workcenter_id.code[0:3] == "SAW"
            ):
                ret = size_list[fieldnum].strip()
        return ret

    def _get_raw_length(self, record):
        ret = 0
        for recid in record.production_id.move_raw_ids:
            strchk = recid.product_id.name
            size_list = strchk.split(",")
            bom_qty = recid.product_qty
            qty_reqd = record.production_id.product_qty
            raw_length = bom_qty / qty_reqd
            classcode = recid.product_id.product_tmpl_id.class_id.name
            if (
                len(size_list) > 2
                and classcode == "RAW MATRL"
                and record.workcenter_id.code[0:3] == "SAW"
            ):
                ret = raw_length
        return ret

    def _get_material(self, record):
        ret = ""
        for recid in record.production_id.move_raw_ids:
            strchk = recid.product_id.name
            fieldnum = 1
            # ugly check
            if "Aluminum Bronze" in strchk:
                fieldnum = 2
            size_list = strchk.split(",")
            classcode = recid.product_id.product_tmpl_id.class_id.name
            if (
                len(size_list) > 2
                and classcode == "RAW MATRL"
                and record.workcenter_id.code[0:3] == "SAW"
            ):
                ret = size_list[fieldnum].strip()
        return ret

    def fill_saw_fields(self):
        domain = [("name", "in", ["SAW TRAK", "SAW DIEMZK", "SAW WIRE", "SAW WDMNT"])]
        for rec in self.search(domain):
            if not rec.material:
                material = self._get_material(rec)
                if material:
                    rec.sudo().write({"material": material})
            if not rec.raw_size:
                raw_size = self._get_raw_size(rec)
                if raw_size:
                    rec.sudo().write({"raw_size": raw_size})
            if not rec.raw_length:
                raw_length = self._get_raw_length(rec)
                if raw_length:
                    rec.sudo().write({"raw_length": raw_length})

    def read(self, fields=None, load="_classic_read"):
        self.fill_saw_fields()
        records = super().read(fields, load)
        return records
