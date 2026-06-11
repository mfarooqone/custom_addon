/** @odoo-module **/

import { cookie } from "@web/core/browser/cookie";
import { browser } from "@web/core/browser/browser";

export function isDarkMode() {
    return cookie.get("color_scheme") === "dark";
}

export function applyThemeClass() {
    document.documentElement.classList.toggle("o_lite_theme_dark", isDarkMode());
}

export function toggleDarkMode() {
    cookie.set("color_scheme", isDarkMode() ? "light" : "dark");
    browser.location.reload();
}
