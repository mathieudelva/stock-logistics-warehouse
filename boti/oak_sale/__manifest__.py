{
    "name": "OAK Sales Additions",
    "version": "16.0.2.0.1",
    "category": "Burr Oak",
    "license": "AGPL-3",
    "summary": "Sales - Partner field additions",
    "author": "Burr Oak Tool, Open Source Integrators",
    "website": "https://www.burroak.com",
    "maintainers": ["emsmith"],
    "depends": [
        "base",
        "sale_stock",
        "oak_permissions",
        "oak_partner",
        "sale_exception",
        "account_financial_risk",
        "sale_stock_picking_note",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_leadtime_message.xml",
        "views/sales.xml",
        "views/res_partner.xml",
        "report/sale_report.xml",
        "report/sale_work_report_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "oak_sale/static/src/css/styles.css",
        ],
    },
    "demo": [],
    "qweb": [],
    "installable": True,
    "application": False,
    "auto_install": True,
}
