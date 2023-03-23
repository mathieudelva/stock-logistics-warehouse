# Copyright (c) Open Value All Rights Reserved

{
    "name": "MRP Planning Engine SCM",
    "summary": "MRP Planning Engine SCM",
    "version": "16.0.1.0",
    "category": "Manufacturing",
    "website": "www.openvalue.cloud",
    "author": "OpenValue",
    "support": "info@openvalue.cloud",
    "license": "Other proprietary",
    "price": 500.00,
    "currency": "EUR",
    "depends": [
        "mrp_planning_engine",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/paper_format.xml",
        #'views/mrp_bom_views.xml',
        "reports/report_mrp_bom_explosion.xml",
        "wizards/mrp_availability_check_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "images": ["static/description/banner.png"],
}
