.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==================
Burr Oak Tool Inc.
==================

This module adds additional fields to partners and sales orders.

Fields:

    Sales Orders:

        partner_ref - related field partner Reference partner_id.ref
        
        shiprefemail - related field partner Shipping Email partner_shipping_id.email
        
        shipref - related field partner Shipping Reference partner_shipping_id.ref
        
        expedite - Boolean field Expedite 

        sales_rep_id - Many2one - External rep attached to this order defaults to Partner extrep_id

        sales_rep_second_id - Many2one - Optional additional External rep attached to this order

Contributors
------------

* Burr Oak Tool <it_systems@burroak.com>
