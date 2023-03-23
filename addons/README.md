# Active Module List

| Module Name                      | Repo Name         | Type      | Usage                                                                                                                          |
| -------------------------------- | ----------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------ |
| oak_boti_ui                      | local             | BOTI      | UI Alterations for BOTI                                                                                                        |
| oak_crm                          | local             | BOTI      | CRM lead field additions                                                                                                       |
| oak_maintenance                  | local             | BOTI      | Sage info for equipment                                                                                                        |
| oak_redis_session                | local             | BOTI      | Redis for session                                                                                                              |
| purchase_request                 | purchase-workflow | OCA       | Allows requests for purchased items from users                                                                                 |
| purchase_request_tier_validation | purchase-workflow | OCA       | Allows purchase requests to have workflows for validation                                                                      |
| base_user_role                   | server-backend    | OCA       | Allows for grouping permissions into user roles that can be applied                                                            |
| auditlog                         | server-tools      | OCA       | Allows deep tracing of data alterations                                                                                        |
| base_cron_exclusion              | server-tools      | OCA       | Limit cron jobs running at the same time for the same thing                                                                    |
| base_exception                   | server-tools      | OCA       | Dependency for all exception modules                                                                                           |
| base_revision                    | server-ux         | OCA       | Dependency for sale_order_revision                                                                                             |
| base_tier_validation             | server-ux         | OCA       | Dependency for all tier validation modules                                                                                     |
| date_range                       | server-ux         | OCA       | Dependency for ?                                                                                                               |
| queue_job                        | queue             | OCA       | A worker queue for long running tasks that are NOT cron jobs                                                                   |
| web_environment_ribbon           | web               | OCA       | marker for dev/test/qa environments, not used in production                                                                    |
| web_refresher                    | web               | OCA       | refresh button for views                                                                                                       |
| mrp_availability_check           | purchased         | Openvalue | Promise delivery date determination by the projected stockquantity compared to customer requested quantity at all BoM’s level. |
| mrp_planning_engine              | purchased         | Openvalue | Provides a full comprehensive tool for managing material requirements planning.                                                |
| mrp_planning_engine_scm          | purchased         | Openvalue | Supports the analysis of the overall supply chain in a warehouse.                                                              |
| mrp_sfc_queue_time_before        | purchased         | Openvalue | Allows queue time before for planning                                                                                          |
| mrp_shop_floor_control           | purchased         | Openvalue | Supports the E2E process starting from the Manufacturing Order Creation to its Closure.                                        |

# Pending Module List

| Module Name                       | Link              | Type | PR or status                                                                                                           |
| --------------------------------- | ----------------- | ---- | ---------------------------------------------------------------------------------------------------------------------- |
| account_analytic_wip              | account-analytic  | OCA  | https://github.com/OCA/account-analytic/pull/540                                                                       |
| analytic_activity_based_cost      | account-analytic  | OCA  | https://github.com/OCA/account-analytic/pull/538                                                                       |
| mrp_analytic                      | account-analytic  | OCA  | https://github.com/OCA/account-analytic/pull/494                                                                       |
| mrp_analytic_child_mo             | account-analytic  | OCA  | NOT STARTED                                                                                                            |
| mrp_analytic_sale_project         | account-analytic  | OCA  | NOT STARTED                                                                                                            |
| purchase_deposit                  | purchase-workflow | OCA  | https://github.com/OCA/purchase-workflow/pull/1751 (purchase_advance_payment IS completed for 16...)                   |
| purchase_delivery_split_date      | purchase-workflow | OCA  | https://github.com/OCA/purchase-workflow/pull/1687                                                                     |
| purchase_exception                | purchase-workflow | OCA  | https://github.com/OCA/purchase-workflow/pull/1770                                                                     |
| purchase_location_by_line         | purchase-workflow | OCA  | https://github.com/OCA/purchase-workflow/pull/1686                                                                     |
| purchase_order_line_menu          | purchase-workflow | OCA  | NOT STARTED                                                                                                            |
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
| web_company_color                 | web               | OCA  | https://github.com/OCA/web/pull/2449                                                                                   |

Note there's some ugliness with the mrp_analytic migration as the analytic_account_id
was added to the MO in 16
