{
    "name": "Burr Oak Tool - BoM Custom Reports",
    "version": "16.0.1.0.0",
    "category": "https://www.burroak.com",
    "author": "Burr Oak Tool, Open Source Integrators",
    "website": "https://www.burroak.com",
    "license": "LGPL-3",
    "summary": "MRP add detail number + custom reports",
    "maintainers": ["Burr Oak Tool"],
    "depends": ["oak_product"],
    "data": [
        "data/report_paperformat_data.xml",
        "views/mrp_view.xml",
        "views/report_mrpbomstructure.xml",
        "report/mrp_report_views_main.xml",
        "report/mrp_report_bom_flat.xml",
        "report/mrp_report_bom_multi.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "oak_mrp_bom_detail/static/src/xml/template.xml",
        ],
    },
}
