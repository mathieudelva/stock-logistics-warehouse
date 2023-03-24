# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Oak Partner Additions",
    "summary": """
        Adds tracking and additional fields to Partners""",
    "description": """
        Added Fields:
          street3, street4, user_id (salesperson per company),
          external sales rep id, is external rep, parent account reference

        Tracked Fields:
          name, street, street2, city, state_id, zip, country_id
          legal_id_number,property_supplier_payment_term_id,
          property_payment_method_id,property_account_receivable_id
          property_account_payable_id

          Type and parent_id "pull" from parent_ref if needed

          Helper method to get list of followers who are NOT internal users

          View changes for new fields

    """,
    "version": "16.0.1.0.0",
    "category": "Sales",
    "license": "Other proprietary",
    "author": "Burr Oak Tool Inc",
    "website": "https://www.burroak.com",
    "maintainers": ["emsmith"],
    "depends": [
        "base",
        "contacts",
    ],
    "data": [
        "views/partner.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
