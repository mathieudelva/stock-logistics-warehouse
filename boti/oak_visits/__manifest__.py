{
    "name": "Oak Visits",
    "summary": """
        Additions to the Site Visit Management for Projects or sales""",
    "description": """
        Additions to the Site Visit Management for Projects or sales
        Visit assesment, product status and reasons

    """,
    "version": "16.0.1.0.0",
    "category": "Project",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "license": "Other proprietary",
    "maintainers": ["burroak"],
    "depends": ["acs_visits", "project"],
    "data": [
        "security/ir.model.access.csv",
        "views/visit_menu.xml",
        "views/visit_assessment.xml",
        "views/visit_product_status.xml",
        "views/visit_reason.xml",
        "views/visit_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
