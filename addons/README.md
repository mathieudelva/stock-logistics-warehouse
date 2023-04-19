# Active Module List

| Module Name                              | Repo Name                 | Source    | Usage                                                                                                  |
| ---------------------------------------- | ------------------------- | --------- | ------------------------------------------------------------------------------------------------------ |
| account_analytic_wip                     | account-analytic          | OCA       | track and report work in progress and variances                                                        |
| account_banking_mandate                  | account-analytic          | OCA       | Generic model for banking mandates                                                                     |
| account_financial_risk                   | credit-control            | OCA       | limit a partner's financial risk                                                                       |
| account_journal_lock_date                | account-financial-tools   | OCA       | Lock each accounting journal independently                                                             |
| account_mail_autosubscribe               | account-invoicing         | OCA       | configure partners that will be automatically in copy of their company's Invoices                      |
| account_payment_batch_process_discount   | account-payment           | OCA       | define discounts for early payment and apply them on batch payments                                    |
| acs_visits                               | purchased                 | ACS       | Site Visit Management for Projects or sales                                                            |
| analytic_activity_based_cost             | account-analytic          | OCA       | generating costs are represented as Analytic Items                                                     |
| auditlog                                 | server-tools              | OCA       | Allows deep tracing of data alterations                                                                |
| auth_user_case_insensitive               | server-auth               | OCA       | makes user logins case insensitive                                                                     |
| base_cron_exclusion                      | server-tools              | OCA       | Limit cron jobs running at the same time for the same thing                                            |
| base_exception                           | server-tools              | OCA       | Dependency for all exception modules                                                                   |
| base_revision                            | server-ux                 | OCA       | Dependency for sale_order_revision                                                                     |
| base_tier_validation                     | server-ux                 | OCA       | Dependency for all tier validation modules                                                             |
| base_user_role                           | server-backend            | OCA       | Allows for grouping permissions into user roles that can be applied                                    |
| base_user_role_company                   | server-backend            | OCA       | Allows for grouping permissions into user roles that can be applied                                    |
| bryntum_gantt_enterprise                 | purchased                 | Bryntum   | Manage and visualise your projects with the fastest Gantt chart on the web                             |
| fetchmail_notify_error_to_sender         | server-tools              | OSI       | NDR messages for emails                                                                                |
| l10n_us_check_printing_micr              | osi-addons                | OSI       | links the manufacturing area with analytic management                                                  |
| mail_autosubscribe                       | social                    | OSI       | configure partners that will be automatically in copy                                                  |
| mrp_account_analytic                     | manufacture               | OCA       | Generates Analytic Items during manufacturing operations                                               |
| mrp_account_analytic_wip                 | manufacture               | OCA       | Generate WIP and Variance journal entries for mfg. consumptions                                        |
| mrp_analytic                             | account-analytic          | OCA       | links the manufacturing area with analytic management                                                  |
| mrp_analytic_child_mo                    | account-analytic          | OCA       | set on those MOs the same Analytic Account as in parent MO for MTO                                     |
| mrp_analytic_sale_project                | account-analytic          | OCA       | MOs Analytic Account to the Sales Order one                                                            |
| mrp_availability_check                   | purchased                 | Openvalue | Promise delivery date by the projected stock quantity to requested quantity at all BoM’s level.        |
| mrp_bom_tracking                         | manufacture               | OCA       | track visibility formrp boms, log notes for any change in the components                               |
| mrp_planning_engine                      | purchased                 | Openvalue | Provides a full comprehensive tool for managing material requirements planning.                        |
| mrp_planning_engine_scm                  | purchased                 | Openvalue | Supports the analysis of the overall supply chain in a warehouse.                                      |
| mrp_sfc_queue_time_before                | purchased                 | Openvalue | Allows queue time before for planning                                                                  |
| mrp_shop_floor_control                   | purchased                 | Openvalue | Supports the E2E process starting from the Manufacturing Order Creation to its Closure.                |
| oak_account_analytic_group               | oak                       | BOTI      | Accounting customization analytic group used as sales type.                                            |
| oak_account_reports_enhancement          | oak                       | BOTI      | Accounting Reports Enhancement                                                                         |
| oak_api                                  | oak                       | BOTI      | Adds API endpoints for the oak app                                                                     |
| oak_boti_ui                              | oak                       | BOTI      | UI Alterations for BOTI                                                                                |
| oak_crm                                  | oak                       | BOTI      | CRM lead field additions                                                                               |
| oak_helpdesk_eco                         | oak                       | BOTI      | Adds create eco from helpdesk ticket, links tickets to plm/eco records                                 |
| oak_helpdesk_project                     | oak                       | BOTI      | Adds create project from helpdesk ticket, links tickets to project records                             |
| oak_helpdesk_sales_order                 | oak                       | BOTI      | Adds create Sales Order from helpdesk ticket, links tickets to sales order records                     |
| oak_helpdesk_task                        | oak                       | BOTI      | Adds create task from helpdesk ticket, links tickets to task records                                   |
| oak_legacy                               | oak                       | BOTI      | Product OAK Legacy Data                                                                                |
| oak_maintenance                          | oak                       | BOTI      | Sage info for equipment                                                                                |
| oak_mrp                                  | oak                       | BOTI      | Adds additional fields to production, workcenters, and work orders                                     |
| oak_mrp_eco                              | oak                       | BOTI      | This module allows additional products on eco                                                          |
| oak_mrp_bom_report                       | oak                       | BOTI      | MRP add detail number + custom reports                                                                 |
| oak_partner                              | oak                       | BOTI      | Partner additional fields and tracking                                                                 |
| oak_permissions                          | oak                       | BOTI      | This module controls all custom permissions for boti                                                   |
| oak_product                              | oak                       | BOTI      | Adds a Product App with links to product listing, adds additional product fields                       |
| oak_project                              | oak                       | BOTI      | Adds tracking for some project fields                                                                  |
| oak_redis_session                        | oak                       | BOTI      | Redis for session                                                                                      |
| oak_revaluation_job_queue                | oak                       | BOTI      | Queue job override for the cost roll                                                                   |
| oak_sale                                 | oak                       | BOTI      | Additional sales fields                                                                                |
| oak_sale_pool                            | oak                       | BOTI      | This module adds additional fields sales orders and analytic account automated creation.               |
| oak_sale_warranty                        | oak                       | BOTI      | Adds user driven text areas to sales orders                                                            |
| oak_stock                                | oak                       | BOTI      | Inventory configuration and customization                                                              |
| oak_visits                               | oak                       | BOTI      | BOTI Customizations for acs_visits                                                                     |
| partner_affiliate                        | partner-contact           | OCA       | moves companies to affiliates tab out of contacts tab                                                  |
| partner_identification                   | partner-contact           | OCA       | manage all sort of identification numbers and certificates which are assigned to a partner             |
| partner_stage                            | partner-contact           | OCA       | stages for contacts for a lifecycle workflow                                                           |
| partner_tier_validation                  | partner-contact           | OCA       | Adds an approval workflow to Partners                                                                  |
| partner_usps_address_validation          | partner-contact           | OCA       | Module adds a tool to the Contacts page which validates the contact's address                          |
| product_code_unique                      | product-attribute         | OCA       | Set Product Internal Reference as Unique                                                               |
| product_sequence                         | product-attribute         | OCA       | This module allows to associate a sequence to the product reference                                    |
| product_state                            | product-attribute         | OCA       | Module introducing a state field on product template                                                   |
| product_tier_validation                  | product-attribute         | OCA       | Adds an approval workflow to Products                                                                  |
| project_list                             | project                   | OCA       | Projects List View                                                                                     |
| project_role                             | project                   | OCA       | Project role-based roster                                                                              |
| project_template                         | project                   | OCA       | Project Templates                                                                                      |
| purchase_delivery_split_date             | purchase-workflow         | OCA       | Purchase order ship date per line                                                                      |
| purchase_deposit                         | purchase-workflow         | OCA       | purchase order to register deposit similar to that in sales order                                      |
| purchase_exception                       | purchase-workflow         | OCA       | Base Exceptions for purchasing                                                                         |
| purchase_order_line_menu                 | purchase-workflow         | OCA       | Adds a menu item to list all Purchase Order lines                                                      |
| purchase_order_line_price_history        | purchase-workflow         | OCA       | see the price history of a product from a purchase order line                                          |
| purchase_order_type                      | purchase-workflow         | OCA       | configurable _type_ on the purchase orders                                                             |
| purchase_partner_approval                | purchase-workflow         | OCA       | vendor approval workflow                                                                               |
| purchase_picking_state                   | purchase-workflow         | OCA       | Adds a field _Receiption Status_ on purchase orders                                                    |
| purchase_reception_status                | purchase-workflow         | OCA       | Adds a "picking status" field on Purchase Orders                                                       |
| purchase_request                         | purchase-workflow         | OCA       | Allows requests for purchased items from users                                                         |
| purchase_request_department              | purchase-workflow         | OCA       | adds the user department in a new field in the purchase request                                        |
| purchase_request_tier_validation         | purchase-workflow         | OCA       | Allows purchase requests to have workflows for validation                                              |
| purchase_request_type                    | purchase-workflow         | OCA       | configurable _type_ on the purchase request                                                            |
| queue_job                                | queue                     | OCA       | A worker queue for long running tasks that are NOT cron jobs                                           |
| sale_delivery_split_date                 | sale-workflow             | OCA       | date per sales order line                                                                              |
| sale_exception                           | sale-workflow             | OCA       | exceptions for sales orders                                                                            |
| sale_order_line_date                     | sale-workflow             | OCA       | adds a commitment date to each sale order line and propagate it to stock moves and pickings            |
| sale_order_line_menu                     | sale-workflow             | OCA       | adds menu item to view individual sales lines                                                          |
| sale_order_revision                      | sale-workflow             | OCA       | sales order revisions via cancel/new from cancelled                                                    |
| sale_partner_approval                    | sale-workflow             | OCA       | customer approval workflow                                                                             |
| sale_partner_incoterm                    | sale-workflow             | OCA       | incoterms for sales orders and contacts                                                                |
| sale_procurement_group_by_line           | sale-workflow             | OCA       | dep for delivery_split_date                                                                            |
| sale_product_approval                    | sale-workflow             | OCA       | control product activities by candiate status                                                          |
| sale_product_approval_mrp                | sale-workflow             | OCA       | product can be manufactured, a component of a manufacturing order or on a bom in the particular state  |
| sale_product_approval_purchase           | sale-workflow             | OCA       | Purchase Order Product Apploval Workflow                                                               |
| sale_product_approval_stock              | sale-workflow             | OCA       | Delivery Order Approval Workflow                                                                       |
| sale_stock_picking_note                  | sale-workflow             | OCA       | Adds Picking Internal Note and Picking Customer Comments to other info in sales that show on picking   |
| scrap_reason_code                        | stock-logistics-warehouse | OCA       | Adds a reason code for scrapping operations                                                            |
| shipstation_shipping_odoo_integration    | purchased                 | Vraja     | Shipstation shipping integrations                                                                      |
| stock_delivery_note                      | stock-logistics-workflow  | OCA       | Adds a delivery note in stock pickings. Displayed on delivery reports.                                 |
| stock_financial_risk                     | stock-logistics-workflow  | OCA       | Adds a delivery note in stock pickings. Displayed on delivery reports.                                 |
| stock_inventory_revaluation_adjustment   | stock-logistics-warehouse | OCA       | Adds a cost change process workflow to products to allow users to adjust costs in bulk                 |
| stock_inventory_revaluation_mrp          | stock-logistics-warehouse | OCA       | Adds a manufacturing components to see what BoM's/Manufaturing Orders are affected by the cost changes |
| stock_inventory_revaluation_wip          | stock-logistics-warehouse | OCA       | 'Cost Type' and 'Activity Driven Costs' components and bring them into the cost adjustment details     |
| stock_move_location                      | stock-logistics-warehouse | OCA       | This module allows to move all stock in a stock location to an other one.                              |
| stock_no_negative                        | stock-logistics-workflow  | OCA       | Blocks negative stock                                                                                  |
| stock_picking_back2draft                 | stock-logistics-workflow  | OCA       | Cancelled pickings back to draft                                                                       |
| stock_picking_sale_order_link            | stock-logistics-workflow  | OCA       | smart button to Stock Transfers, to open the related Sales Order                                       |
| support_helpdesk_ticket_merge_enterprise | purchased                 | Probuse   | merge helpdesk tickets                                                                                 |
| web_company_color                        | web                       | OCA       | Per company navbar colors                                                                              |
| web_environment_ribbon                   | web                       | OCA       | marker for dev/test/qa environments, not used in production                                            |
| web_m2x_options                          | web                       | OCA       | remove "Create..." and/or "Create and Edit..." entries from many2one drop down                         |
| web_m2x_options_manager                  | web                       | OCA       | allows managing m2x fields directly from the ir.model form view                                        |
| web_notify                               | web                       | OCA       | notify message for queue                                                                               |
| web_refresher                            | web                       | OCA       | refresh button for views                                                                               |
| web_search_with_and                      | web                       | OCA       | press Shift key before searching for and                                                               |
| website_odoo_debranding                  | website                   | OCA       | Allows to turn odoo website links off on website pages                                                 |
