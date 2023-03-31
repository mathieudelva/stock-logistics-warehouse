# Active Module List

| Module Name                              | Repo Name                 | Type      | Usage                                                                                           |
| ---------------------------------------- | ------------------------- | --------- | ----------------------------------------------------------------------------------------------- |
| acs_visits                               | purchased                 | ACS       | Site Visit Management for Projects or sales                                                     |
| auditlog                                 | server-tools              | OCA       | Allows deep tracing of data alterations                                                         |
| base_cron_exclusion                      | server-tools              | OCA       | Limit cron jobs running at the same time for the same thing                                     |
| base_exception                           | server-tools              | OCA       | Dependency for all exception modules                                                            |
| base_revision                            | server-ux                 | OCA       | Dependency for sale_order_revision                                                              |
| base_tier_validation                     | server-ux                 | OCA       | Dependency for all tier validation modules                                                      |
| base_user_role                           | server-backend            | OCA       | Allows for grouping permissions into user roles that can be applied                             |
| bryntum_gantt_enterprise                 | purchased                 | Bryntum   | Manage and visualise your projects with the fastest Gantt chart on the web                      |
| mrp_availability_check                   | purchased                 | Openvalue | Promise delivery date by the projected stock quantity to requested quantity at all BoM’s level. |
| mrp_planning_engine                      | purchased                 | Openvalue | Provides a full comprehensive tool for managing material requirements planning.                 |
| mrp_planning_engine_scm                  | purchased                 | Openvalue | Supports the analysis of the overall supply chain in a warehouse.                               |
| mrp_sfc_queue_time_before                | purchased                 | Openvalue | Allows queue time before for planning                                                           |
| mrp_shop_floor_control                   | purchased                 | Openvalue | Supports the E2E process starting from the Manufacturing Order Creation to its Closure.         |
| oak_boti_ui                              | local                     | BOTI      | UI Alterations for BOTI                                                                         |
| oak_crm                                  | local                     | BOTI      | CRM lead field additions                                                                        |
| oak_partner                              | local                     | BOTI      | Partner additional fields and tracking                                                          |
| oak_maintenance                          | local                     | BOTI      | Sage info for equipment                                                                         |
| oak_redis_session                        | local                     | BOTI      | Redis for session                                                                               |
| oak_visits                               | local                     | BOTI      | BOTI Customizations for acs_visits                                                              |
| product_code_unique                      | product-attribute         | OCA       | Set Product Internal Reference as Unique                                                        |
| product_state                            | product-attribute         | OCA       | Module introducing a state field on product template                                            |
| project_list                             | project                   | OCA       | Projects List View                                                                              |
| project_role                             | project                   | OCA       | Project role-based roster                                                                       |
| project_template                         | project                   | OCA       | Project Templates                                                                               |
| purchase_delivery_split_date             | purchase-workflow         | OCA       | Purchase order ship date per line                                                               |
| purchase_exception                       | purchase-workflow         | OCA       | Base Exceptions for purchasing                                                                  |
| purchase_order_line_menu                 | purchase-workflow         | OCA       | Adds a menu item to list all Purchase Order lines                                               |
| purchase_request                         | purchase-workflow         | OCA       | Allows requests for purchased items from users                                                  |
| purchase_request_tier_validation         | purchase-workflow         | OCA       | Allows purchase requests to have workflows for validation                                       |
| queue_job                                | queue                     | OCA       | A worker queue for long running tasks that are NOT cron jobs                                    |
| scrap_reason_code                        | stock-logistics-warehouse | OCA       | Adds a reason code for scrapping operations                                                     |
| stock_delivery_note                      | stock-logistics-workflow  | OCA       | Adds a delivery note in stock pickings. Displayed on delivery reports.                          |
| stock_no_negative                        | stock-logistics-workflow  | OCA       | Blocks negative stock                                                                           |
| stock_picking_back2draft                 | stock-logistics-workflow  | OCA       | Cancelled pickings back to draft                                                                |
| stock_picking_sale_order_link            | stock-logistics-workflow  | OCA       | smart button to Stock Transfers, to open the related Sales Order                                |
| support_helpdesk_ticket_merge_enterprise | purchased                 | Probuse   | merge helpdesk tickets                                                                          |
| web_company_color                        | web                       | OCA       | Per company navbar colors                                                                       |
| web_environment_ribbon                   | web                       | OCA       | marker for dev/test/qa environments, not used in production                                     |
| web_search_with_and                      | web                       | OCA       | press Shift key before searching for and                                                        |
| web_refresher                            | web                       | OCA       | refresh button for views                                                                        |
| website_odoo_debranding                  | website                   | OCA       | Allows to turn odoo website links off on website pages                                          |

# Pending Module List

| Module Name                       | Link              | Type | PR or status                                                                                                           |
| --------------------------------- | ----------------- | ---- | ---------------------------------------------------------------------------------------------------------------------- |
| account_analytic_wip              | account-analytic  | OCA  | https://github.com/OCA/account-analytic/pull/540                                                                       |
| analytic_activity_based_cost      | account-analytic  | OCA  | https://github.com/OCA/account-analytic/pull/538                                                                       |
| mrp_analytic                      | account-analytic  | OCA  | https://github.com/OCA/account-analytic/pull/494                                                                       |
| mrp_analytic_child_mo             | account-analytic  | OCA  | NOT STARTED                                                                                                            |
| mrp_analytic_sale_project         | account-analytic  | OCA  | NOT STARTED                                                                                                            |
| purchase_deposit                  | purchase-workflow | OCA  | https://github.com/OCA/purchase-workflow/pull/1751 (purchase_advance_payment IS completed for 16...)                   |
| purchase_location_by_line         | purchase-workflow | OCA  | https://github.com/OCA/purchase-workflow/pull/1686                                                                     |
| purchase_order_line_price_history | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
| purchase_order_type               | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
| purchase_partner_approval         | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
| purchase_picking_state            | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
| purchase_reception_status         | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
| purchase_request_department       | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
| purchase_request_type             | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
| auth_user_case_insensitive        | server-auth       | OCA  | https://github.com/OCA/server-auth/pull/479                                                                            |
| user_log_view                     | server-auth       | OCA  | NOT STARTED                                                                                                            |
| base_user_role_company            | server-backend    | OCA  | https://github.com/OCA/server-backend/pull/187 - 15? Stale?                                                            |
| fetchmail_notify_error_to_sender  | server-tools      | OCA  | NOT STARTED                                                                                                            |
| bus_alt_connection                | server-tools      | OCA  | Elizabeth has a ported version of this, maybe to OCa, maybe as oak module instead - not needed until pooler is up (QA) |
| base_import_security_group        | server-ux         | OCA  | NOT STARTED                                                                                                            |

Note there's some ugliness with the mrp_analytic migration as the analytic_account_id
was added to the MO in 16
