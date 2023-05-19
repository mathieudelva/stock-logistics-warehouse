# Copyright (C) 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Oak Account Commercial Invoice report",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Oak Account Commercial Invoice report",
    "author": "Open Source Integrators",
    "maintainers": ["Open Source Integrators"],
    "website": "http://www.opensourceintegrators.com",
    "category": "Accounting",
    "depends": [
        "oak_account",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "reports/commercial_report.xml",
    ],
    "installable": True,
}
