# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    "name": "Merge Helpdesk Support Tickets and Issues",
    "depends": ["helpdesk"],
    "currency": "EUR",
    "price": 49.0,
    "license": "Other proprietary",
    "summary": """This module allow you to merge tickets of your
                helpdesk support system in Odoo Enterprise.""",
    "description": """
helpdesk support ticket
tickets merge
merge tickets
merge ticket
merge support ticket
merge helpdesk support tickets

    """,
    "author": "Probuse Consulting Service Pvt. Ltd.",
    "website": "http://www.probuse.com",
    "images": ["static/description/img.png"],
    # 'live_test_url': 'https://youtu.be/m1FjfRpWzrA',
    "live_test_url": "https://probuseappdemo.com/probuse_apps/support_helpdesk_ticket_merge_enterprise/414",
    "support": "contact@probuse.com",
    "version": "4.8.1",
    "category": "Services/Project",
    "data": [
        "security/ir.model.access.csv",
        "wizard/merge_ticket_wizard.xml",
        "views/helpdesk_ticket_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
