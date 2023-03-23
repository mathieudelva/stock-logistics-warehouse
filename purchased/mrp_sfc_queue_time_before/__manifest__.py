# Copyright (c) Open Value All Rights Reserved

{
    "name": "MRP Shop Floor Queue Time Before",
    "summary": "MRP Shop Floor Control Queue Time Before",
    "version": "16.0.1.0",
    "category": "Manufacturing",
    "website": "www.openvalue.cloud",
    "author": "OpenValue",
    "support": "info@openvalue.cloud",
    "license": "Other proprietary",
    "price": 0.00,
    "currency": "EUR",
    "depends": [
        "mrp_shop_floor_control",
    ],
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_routing_workcenter_views.xml",
        "views/mrp_workorder_views.xml",
        "views/mrp_workorder_midpointscheduling_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "images": ["static/description/banner.png"],
}
