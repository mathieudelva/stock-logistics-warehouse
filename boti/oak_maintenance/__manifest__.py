{
    "name": "Oak Maintenance Additions",
    "summary": """
        Adds additional fields to maintenance equipment""",
    "description": """
        Adds sage number and sage reference for synchronzation of data with our sage install

    """,
    "version": "16.0.1.0.0",
    "category": "Maintenance",
    "license": "Other proprietary",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "maintainers": ["emsmith"],
    "depends": [
        "base",
        "maintenance",
    ],
    "data": ["security/ir.model.access.csv", "views/maintenance_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
