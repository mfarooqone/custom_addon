/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { isDarkMode, toggleDarkMode } from "./theme_mode";

function darkModeMenuItem() {
    return {
        type: "item",
        id: "lite_theme_dark_mode",
        description: isDarkMode() ? _t("Light mode") : _t("Dark mode"),
        callback: () => toggleDarkMode(),
        sequence: 45,
    };
}

registry.category("user_menuitems").add("lite_theme_dark_mode", darkModeMenuItem);
