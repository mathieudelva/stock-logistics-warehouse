# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Oak Account Customization",
    "version": "16.0.1.2.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators",
    "maintainers": ["Open Source Integrators"],
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": [
        "account_accountant",
        "account_check_printing",
        "account_followup",
        "account_intrastat",
        "delivery",
        "l10n_us_check_printing_micr",
        "mrp",
        "purchase",
        "oak_sale",
        "partner_stage",
    ],
    "data": [
        "views/account_move.xml",
        "views/account_move_line.xml",
        "views/account_payment_views.xml",
        "views/partner_view.xml",
    ],
    "installable": True,
}
