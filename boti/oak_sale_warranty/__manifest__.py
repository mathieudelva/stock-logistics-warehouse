{
    "name": "Oak Sale Warranty Text",
    "summary": """
        Adds user driven text areas to sales orders""",
    "description": """
        Can be set as a default per company, can also set per sales order

    """,
    "version": "16.0.1.0.0",
    "category": "Sales",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "license": "Other proprietary",
    "maintainers": ["emsmith"],
    "depends": ["oak_sale"],
    "data": [
        "security/ir.model.access.csv",
        "report/sale_report_templates.xml",
        "views/sales.xml",
        "views/warranty_policy.xml",
        "report/sale_report_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "qweb": [],
    "installable": True,
    "application": False,
    "auto_install": True,
}
