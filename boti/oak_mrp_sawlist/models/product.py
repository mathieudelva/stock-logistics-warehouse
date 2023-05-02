from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template"
    _order = "name"

    @api.depends(
        "product_finish_height",
        "product_finish_width",
        "product_finish_length",
        "product_finish_length_tolerance_id",
        "product_finish_width_tolerance_id",
        "product_finish_height_tolerance_id",
    )
    def _compute_finish_size(self):
        lformat = "{0:.3f}"
        hformat = "{0:.3f}"
        wformat = "{0:.3f}"
        for record in self:
            len_tol = ""
            if record.product_finish_length_tolerance_id:
                len_tol = record.product_finish_length_tolerance_id.name
                if record.product_finish_length_tolerance_id.nformat:
                    lformat = record.product_finish_length_tolerance_id.nformat
            wid_tol = ""
            if record.product_finish_width_tolerance_id:
                wid_tol = record.product_finish_width_tolerance_id.name
                if record.product_finish_width_tolerance_id.nformat:
                    wformat = record.product_finish_width_tolerance_id.nformat
            hi_tol = ""
            if record.product_finish_height_tolerance_id:
                hi_tol = record.product_finish_height_tolerance_id.name
                if record.product_finish_height_tolerance_id.nformat:
                    hformat = record.product_finish_height_tolerance_id.nformat

            finish_size = ""
            if record.product_finish_height:
                finish_size = hformat.format(record.product_finish_height)
                if hi_tol:
                    finish_size += " " + str(
                        record.product_finish_height_tolerance_id.name
                    )
            if record.product_finish_width:
                finish_size += " X " + wformat.format(record.product_finish_width)
                if wid_tol:
                    finish_size += " " + str(
                        record.product_finish_width_tolerance_id.name
                    )
            if record.product_finish_length:
                finish_size += " X " + lformat.format(record.product_finish_length)
                if len_tol:
                    finish_size += " " + str(
                        record.product_finish_length_tolerance_id.name
                    )
            # Ensure value is always set
            record.finish_size = finish_size

    product_finish_length_tolerance_id = fields.Many2one(
        "oak.tolerance", string="Length Tolerance", help="Length Tolerance"
    )
    product_finish_width_tolerance_id = fields.Many2one(
        "oak.tolerance", string="Width Tolerance", help="Width Tolerance"
    )
    product_finish_height_tolerance_id = fields.Many2one(
        "oak.tolerance", string="Height Tolerance", help="Height Tolerance"
    )

    product_finish_length = fields.Float(string="Length", digits=(12, 4))
    product_finish_height = fields.Float(string="Height", digits=(12, 4))
    product_finish_width = fields.Float(string="Width", digits=(12, 4))

    finish_size = fields.Char(
        string="Finished size", compute=_compute_finish_size, store=True
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends(
        "product_finish_height",
        "product_finish_width",
        "product_finish_length",
        "product_finish_length_tolerance_id",
        "product_finish_width_tolerance_id",
        "product_finish_height_tolerance_id",
    )
    def _compute_finish_size(self):
        lformat = "{0:.3f}"
        hformat = "{0:.3f}"
        wformat = "{0:.3f}"
        for record in self:
            len_tol = ""
            if record.product_finish_length_tolerance_id:
                len_tol = record.product_finish_length_tolerance_id.name
                if record.product_finish_length_tolerance_id.nformat:
                    lformat = record.product_finish_length_tolerance_id.nformat
            wid_tol = ""
            if record.product_finish_width_tolerance_id:
                wid_tol = record.product_finish_width_tolerance_id.name
                if record.product_finish_width_tolerance_id.nformat:
                    wformat = record.product_finish_width_tolerance_id.nformat
            hi_tol = ""
            if record.product_finish_height_tolerance_id:
                hi_tol = record.product_finish_height_tolerance_id.name
                if record.product_finish_height_tolerance_id.nformat:
                    hformat = record.product_finish_height_tolerance_id.nformat

            finish_size = ""
            if record.product_finish_height:
                finish_size = hformat.format(record.product_finish_height)
                if hi_tol:
                    finish_size += " " + str(
                        record.product_finish_height_tolerance_id.name
                    )
            if record.product_finish_width:
                finish_size += " X " + wformat.format(record.product_finish_width)
                if wid_tol:
                    finish_size += " " + str(
                        record.product_finish_width_tolerance_id.name
                    )
            if record.product_finish_length:
                finish_size += " X " + lformat.format(record.product_finish_length)
                if len_tol:
                    finish_size += " " + str(
                        record.product_finish_length_tolerance_id.name
                    )
            # Ensure value is always set
            record.finish_size = finish_size

    product_finish_length_tolerance_id = fields.Many2one(
        "oak.tolerance", string="Length Tolerance", help="Length Tolerance"
    )
    product_finish_width_tolerance_id = fields.Many2one(
        "oak.tolerance", string="Width Tolerance", help="Width Tolerance"
    )
    product_finish_height_tolerance_id = fields.Many2one(
        "oak.tolerance", string="Height Tolerance", help="Height Tolerance"
    )

    product_finish_length = fields.Float(string="Length", digits=(12, 4))
    product_finish_height = fields.Float(string="Height", digits=(12, 4))
    product_finish_width = fields.Float(string="Width", digits=(12, 4))
    finish_size = fields.Char(
        string="Finished size", compute=_compute_finish_size, store=True
    )

    def _default_size_fields(self, fvals, record):
        if not record.product_finish_length:
            if record.product_tmpl_id.product_finish_length:
                fvals[
                    "product_finish_length"
                ] = record.product_tmpl_id.product_finish_length
        if not record.product_finish_width:
            if record.product_tmpl_id.product_finish_width:
                fvals[
                    "product_finish_width"
                ] = record.product_tmpl_id.product_finish_width
        if not record.product_finish_height:
            if record.product_tmpl_id.product_finish_height:
                fvals[
                    "product_finish_height"
                ] = record.product_tmpl_id.product_finish_height

    def _default_length_tolerance(self, fvals, record):
        if not record.product_finish_length_tolerance_id.id:
            if record.product_tmpl_id.product_finish_length_tolerance_id.id:
                fvals[
                    "product_finish_length_tolerance_id"
                ] = record.product_tmpl_id.product_finish_length_tolerance_id.id

    def _default_width_tolerance(self, fvals, record):
        if not record.product_finish_width_tolerance_id.id:
            if record.product_tmpl_id.product_finish_width_tolerance_id.id:
                fvals[
                    "product_finish_width_tolerance_id"
                ] = record.product_tmpl_id.product_finish_width_tolerance_id.id

    def _default_height_tolerance(self, fvals, record):
        if not record.product_finish_height_tolerance_id.id:
            if record.product_tmpl_id.product_finish_height_tolerance_id.id:
                fvals[
                    "product_finish_height_tolerance_id"
                ] = record.product_tmpl_id.product_finish_height_tolerance_id.id

    def _default_finish_dimensions(self, fvals, record):
        self._default_size_fields(fvals, record)
        self._default_length_tolerance(fvals, record)
        self._default_width_tolerance(fvals, record)
        self._default_height_tolerance(fvals, record)
        if fvals:
            record.write(fvals)

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        # if variants default finish size fields to product template
        fvals = {}
        for record in self:
            if not record.product_finish_length:
                if record.product_tmpl_id.product_finish_length:
                    fvals[
                        "product_finish_length"
                    ] = record.product_tmpl_id.product_finish_length
            if not record.product_finish_width:
                if record.product_tmpl_id.product_finish_width:
                    fvals[
                        "product_finish_width"
                    ] = record.product_tmpl_id.product_finish_width
            if not record.product_finish_height:
                if record.product_tmpl_id.product_finish_height:
                    fvals[
                        "product_finish_height"
                    ] = record.product_tmpl_id.product_finish_height
            if not record.finish_size:
                if record.product_tmpl_id.finish_size:
                    fvals["finish_size"] = record.product_tmpl_id.finish_size
            if not record.product_finish_length_tolerance_id.id:
                if record.product_tmpl_id.product_finish_length_tolerance_id.id:
                    fvals[
                        "product_finish_length_tolerance_id"
                    ] = record.product_tmpl_id.product_finish_length_tolerance_id.id
            if fvals:
                record.write(fvals)
        return res
