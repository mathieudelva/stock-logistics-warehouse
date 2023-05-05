{
    "name": "Oak Product Additions",
    "summary": """
        Adds a Product App with links to product listing, adds additional product fields""",
    "description": """
        Product App and Adjustments

        1. Sequence seq_product_product for products
        2. Add classcode, detail number, generic name, and material as tables
        3. Add classcode, detail number, generic name, and material linked to product.template
        4. Add engineering note as an additional text field

        Add tracking for:
        categ_id, allow_negative_stock, company_id, uom_id, uom_po_id,
        proposed_cost on product.template

        Add tracking for:
        standard_price, default_code, proposed_cost on product.product

    """,
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "license": "Other proprietary",
    "maintainers": ["emsmith"],
    "depends": [
        "base",
        "product",
        "product_state",
        "sale_product_approval",
        "sale_product_approval_mrp",
        "product_tier_validation",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/product.xml",
        "views/material.xml",
        "views/classcode.xml",
        "views/detailnumber.xml",
        "views/genericname.xml",
    ],
    "installable": True,
    "application": False,
}
