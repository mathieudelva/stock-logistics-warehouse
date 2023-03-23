{
    "name": "Oak Manufacturing Additions",
    "summary": """
        Adds additional fields to production, workcenters, and work orders""",
    "description": """
        Adds External ref to bom lines
        Adds MO Hold and Hold reason fields to production (MO) line
        Adds department to workcenter
        Adds multiple fields to workorder
          computed/linked: mto_origin, analytic_account_id, mo_hold, mo_hold_reason
          cnc_program, department_id, department, detail_number

          new fields: machine_id, employee_id, note

    """,
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "license": "Other proprietary",
    "maintainers": ["emsmith"],
    "depends": [
        "mrp",
        "oak_product",
    ],
    "data": [
        "views/mrp_production.xml",
        "report/mrp_production_templates.xml",
        "views/mrp_workorder.xml",
        "views/mrp_workcenter.xml",
    ],
    "installable": True,
    "auto_install": False,
}
