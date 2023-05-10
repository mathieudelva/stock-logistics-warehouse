{
    "name": "Oak CRM Additions",
    "summary": "Adds additional fields to CRM sales leads",
    "description": """
        Adds Product Family Category and Product Family model types
        Adds Product family and category to crm leads

    """,
    "version": "16.0.1.0.0",
    "category": "Sales",
    "license": "Other proprietary",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "maintainers": ["emsmith"],
    "depends": ["crm", "oak_permissions", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_lead.xml",
        "views/product_family_category.xml",
        "views/product_family.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
