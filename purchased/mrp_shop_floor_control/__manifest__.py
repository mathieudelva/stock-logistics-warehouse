# Copyright (c) Open Value All Rights Reserved

{
    "name": "MRP Shop Floor Control",
    "summary": "MRP Shop Floor Control",
    "version": "16.0.1.0",
    "category": "Manufacturing",
    "website": "www.openvalue.cloud",
    "author": "OpenValue",
    "support": "info@openvalue.cloud",
    "license": "Other proprietary",
    "price": 3000.00,
    "currency": "EUR",
    "depends": [
        "mrp_workorder",
        "resource",
    ],
    "demo": [],
    "data": [
        "security/mrp_workorder_confirmation_security.xml",
        "security/ir.model.access.csv",
        "views/stock_warehouse_views.xml",
        "views/mrp_floating_times_views.xml",
        "views/mrp_workcenter_team_views.xml",
        #'views/ir_attachment_views.xml',
        "views/mrp_tool_views.xml",
        "views/mrp_workcenter_views.xml",
        "views/mrp_bom_views.xml",
        "views/mrp_routing_workcenter_views.xml",
        "views/mrp_workorder_views.xml",
        #'views/mrp_workorder_midpointscheduling_views.xml',
        "views/mrp_workcenter_capacity_load_views.xml",
        "wizards/mrp_starting_views.xml",
        "wizards/mrp_confirmation_views.xml",
        "wizards/mrp_closing_views.xml",
        "wizards/mrp_capacity_check_views.xml",
        "views/mrp_production_views.xml",
    ],
    "external_dependencies": {
        "python": ["plotly==5.13.1"],
    },
    "post_init_hook": "post_init_hook",
    "assets": {
        "web.assets_backend": [
            "mrp_shop_floor_control/static/src/js/widget_plotly.esm.js",
            "mrp_shop_floor_control/static/src/js/widget_plotly.xml",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
    "images": ["static/description/banner.png"],
}
