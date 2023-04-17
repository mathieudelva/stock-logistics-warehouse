.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==================
Burr Oak Tool Inc.
==================

This module adds additional fields sales orders and analytic account automated creation.

Fields:

    Sales Orders:

        pool - one2many analytic account group

        custom_aa_name - text, Custom Account Analytic Name

        use_custom_name - bool, checkbox to use custom name

        analytic_plan_id - m2o, links to a plan trough analytic account

    Sales Orders:

        sale_line_analytic_plan_id - m2o, link to analytic plan


Contributors
------------

* Burr Oak Tool <it_systems@burroak.com>
