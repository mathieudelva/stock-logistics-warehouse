/** @odoo-module **/

// From https://github.com/OCA/server-brand/blob/15.0/disable_odoo_online/static/src/js/user_menu_items.esm.js

import {registry} from "@web/core/registry";
// Needed so that this is run after adding the menu entries
import {user_menu_items} from "@web/webclient/user_menu/user_menu_items"; // eslint-disable-line no-unused-vars

registry.category("user_menuitems").remove("documentation");
registry.category("user_menuitems").remove("support");
registry.category("user_menuitems").remove("odoo_account");