{
    "name": "Oak Product Additions",
    "summary": """
        Adds a Product App with links to product listing, adds additional product fields""",
    "description": """
        Product App and Adjustments

        1. Sequence seq_product_product for products


        1. New Fields:

    """,
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "license": "Other proprietary",
    "maintainers": ["emsmith"],
    "depends": [
        "base",
        # "sale",
        # "product",
        # "product_sequence",
        # "product_state",
        # "product_tier_validation",
        # "sale_product_approval",
        # "sale_product_approval_mrp",
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
