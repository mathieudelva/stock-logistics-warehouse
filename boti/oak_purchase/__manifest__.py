{
    "name": "OAK Purchase Additions",
    "version": "16.0.1.0.0",
    "category": "Purchase",
    "license": "Other proprietary",
    "summary": "Purchase Modifications",
    "author": "Burr Oak Tool, Open Source Integrators",
    "website": "https://www.burroak.com",
    "maintainers": ["rlopez"],
    "depends": [
        # Core modules
        "purchase",
        # OCA modules
        "purchase_cancel_reason",
        "purchase_delivery_split_date",
        # "purchase_last_price_info", - still broken in multicompany
        "purchase_location_by_line",
        #"purchase_open_qty",
        "purchase_order_line_menu",
        "purchase_order_line_price_history",
        "purchase_order_type",
        "purchase_picking_state",
        "purchase_request",
        "purchase_request_department",
        "purchase_request_tier_validation",
        "purchase_request_type",
        "purchase_reception_status",
        # Purchased modules
        "merge_purchase_order",
    ],
    "data": [
        "views/purchase.xml",
        "data/mail_template_purchase_confirmation.xml",
        "views/purchase_portal.xml",
        "views/product_view.xml",
        "report/purchase_order_templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
