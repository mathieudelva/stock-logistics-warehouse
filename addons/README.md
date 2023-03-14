# Active Module List

Module Name | Repo Name | Type | Usage
--- | --- | --- | ---
oak_boti_ui | local | BOTI | UI Alterations for BOTI
oak_redis_session | local | BOTI | Redis for session storage
base_revision| server-ux | OCA | Dependency for revision modules
base_tier_validation| server-ux | OCA |
date_range| server-ux | OCA |
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
base_import_security_group | server-ux | OCA | NOT STARTED
web_company_color | web | OCA | https://github.com/OCA/web/pull/2449

Note there's some ugliness with the mrp_analytic migration as the analytic_account_id was added to the MO in 16