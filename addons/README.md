# Active Module List

Module Name | Repo Name | Type | Usage
--- | --- | --- | ---
oak_boti_ui | local | BOTI | UI Alterations for BOTI
oak_redis_session | local | BOTI | Redis for session storage
base_user_role | server-backend | OCA | Allows for grouping permissions into user roles that can be applied
auditlog | server-tools | OCA | Allows deep tracing of data alterations
base_cron_exclusion | server-tools | OCA | Limit cron jobs running at the same time for the same thing
base_exception | server-tools | OCA | Dependency for all exception modules
base_revision| server-ux | OCA | Dependency for sale_order_revision
base_tier_validation| server-ux | OCA | Dependency for all tier validation modules
date_range| server-ux | OCA | Dependency for ?
queue_job | queue | OCA | A worker queue for long running tasks that are NOT cron jobs
web_environment_ribbon | web | OCA | marker for dev/test/qa environments, not used in production
web_refresher | web | OCA | refresh button for views
website_odoo_debranding | website | OCA | Remove odoo link on websites

# Pending Module List
Module Name | Link | Type | PR or status
--- | --- | --- | ---
account_analytic_wip | account-analytic | OCA | https://github.com/OCA/account-analytic/pull/540
analytic_activity_based_cost| account-analytic | OCA | https://github.com/OCA/account-analytic/pull/538
mrp_analytic | account-analytic | OCA | https://github.com/OCA/account-analytic/pull/494
mrp_analytic_child_mo | account-analytic | OCA | NOT STARTED
mrp_analytic_sale_project| account-analytic | OCA | NOT STARTED
base_user_role_company | server-backend | OCA | https://github.com/OCA/server-backend/pull/187 - 15? Stale?
fetchmail_notify_error_to_sender | server-tools | OCA | NOT STARTED
bus_alt_connection | server-tools | OCA | Elizabeth has a ported version of this, maybe to OCa, maybe as oak module instead - not needed until pooler is up (QA)
base_import_security_group | server-ux | OCA | NOT STARTED
web_company_color | web | OCA | https://github.com/OCA/web/pull/2449

Note there's some ugliness with the mrp_analytic migration as the analytic_account_id was added to the MO in 16
