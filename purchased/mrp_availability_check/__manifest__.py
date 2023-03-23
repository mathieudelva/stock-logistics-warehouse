# Copyright (c) Open Value All Rights Reserved

{
    "name": "MRP Availability Check",
    "summary": "MRP Availability Check",
    "version": "16.0.1.0",
    "category": "Manufacturing",
    "website": "www.openvalue.cloud",
    "author": "OpenValue",
    "support": "info@openvalue.cloud",
    "license": "Other proprietary",
    "price": 500.00,
    "currency": "EUR",
    "depends": [
        "mrp",
        "mrp_subcontracting",
        "purchase_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/paper_format.xml",
        "reports/report_mrp_bom_explosion.xml",
        "reports/report_mrp_availability_check.xml",
        "wizards/mrp_availability_check_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "images": ["static/description/banner.png"],
}
