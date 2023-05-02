.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==================
Burr Oak Tool Inc.
==================

This module creates a view for sawlist, adds tolerances to mrp & other additional fields

Fields:

    mrp_workorder:

        finish_size = finish size of product

        material = text, material type

        raw_size = size of raw material

        raw_length = length of raw material

        ovr_qty = override qty
    
    oak_tolerance:

        name = tolerance name

        nformat = number format

        description = tolerance description

    product_template:

        product_finish_length_tolerance_id = Length Tolerance

        product_finish_width_tolerance_id = Width Tolerance

        product_finish_height_tolerance_id = Height Tolerance

        product_finish_length = Finish Length

        product_finish_height = Finish Height

        product_finish_width = Finish Width

        finish_size = Finish Size



    product_product:

        product_finish_length_tolerance_id = Length Tolerance

        product_finish_width_tolerance_id = Width Tolerance

        product_finish_height_tolerance_id = Height Tolerance

        product_finish_length = Finish Length

        product_finish_height = Finish Height

        product_finish_width = Finish Width

        finish_size = Finish Size

    View:

        Saw Work Order = found in Manufacturing->Operations->Saw Work Orders


Contributors
------------

* Burr Oak Tool <it_systems@burroak.com>
