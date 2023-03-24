{
    "name": "Gantt View PRO (Enterprise)",
    "summary": """
    Manage and visualise your projects with the fastest Gantt chart on the web.
    """,
    "description": """
    Bryntum Gantt chart is the most powerful Gantt component available. It has a massive set of features that will cover all your project management needs.
    """,
    "author": "Bryntum AB",
    "website": "https://www.bryntum.com/forum/viewforum.php?f=58",
    # Categories can be used to filter modules in modules listing
    # for the full list
    "category": "Project",
    "version": "2.0.1",
    "price": 599.00,
    "currency": "EUR",
    "license": "Other proprietary",
    "support": "odoosupport@bryntum.com",
    "live_test_url": "https://odoo-gantt.bryntum.com",
    # any module necessary for this one to work correctly
    "depends": ["base", "web", "project", "project_enterprise"],
    "images": [
        "images/banner.png",
        "images/main_screenshot.png",
        "images/reschedule.gif",
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/project_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "application": True,
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/bryntum_gantt_enterprise/static/src/js/main.js",
            "/bryntum_gantt_enterprise/static/src/css/main.css",
        ]
    },
}
