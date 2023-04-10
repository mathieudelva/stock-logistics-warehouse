{
    "name": "OAK Legacy Data",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "Burr Oak Tool Inc.",
    "website": "https://www.burroak.com",
    "license": "Other proprietary",
    "summary": "Product OAK Legacy Data",
    "maintainers": ["emsmith", "leichorn", "rlopez", "BOTI"],
    "depends": ["oak_product", "oak_mrp"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menus.xml",
        "views/product.xml",
        "views/mrp_legacy.xml",
        "views/product_legacy.xml",
        "views/product_combine.xml",
        "views/product_legacy_uom.xml",
        "wizard/message.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
