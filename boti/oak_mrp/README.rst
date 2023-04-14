.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==================
Burr Oak Tool Inc.
==================

This module adds additional fields to manufacturing & includes Analytic Account on main report

Fields:

    mrp_bom:
        
        detail_id - Product detail number

    mrp_bom_line:
        
        external_ref - used for migration purposes

        detail_id - Product detail number

    mrp_production:
        
        mo_hold - Checkbox to manually put mo on hold

        mo_hold_reason - required text field when mo on hold is checked
        
    mrp_workcenter:

        department_id - Department
    
    mrp_workorder:

        mto_origin - MTO Origin

        analytic_account_id - Product Analytic Account

        mo_hold - mo on hold from mrp_production

        mo_hold_reason - mo on hold reason from mrp_production

        detail_number - Product detail number

        machine_id - A way to link maintenance equipment

        assigned_employee_id - employee assigned to mrp_workorder

        note - simple text field, way to add comments to workorder

        cnc_program - link to cnc cnc_program

        department_id - link to department id

        department - if we use department_id we get the whole path of department, 
        this is a simple field to only get the last department name



Contributors
------------

* Burr Oak Tool <it_systems@burroak.com>
