/** @odoo-module **/

import { Component, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";
import { hasTouch } from "@web/core/browser/feature_detection";
import { isDarkMode as isDarkModeEnabled, toggleDarkMode } from "../theme/theme_mode";

export class HomeMenu extends Component {
    static template = "community_enterprise_theme_lite_pr.HomeMenu";
    static props = {
        onAppClick: { type: Function, optional: true },
    };

    setup() {
        this.menuService = useService("menu");
        this.ui = useService("ui");

        this.searchInputRef = useRef("searchInput");

        onMounted(() => {
            if (!hasTouch()) {
                this._focusInput();
            }
        });
    }

    get appsAndMenuItems() {
        const menuTree = this.menuService.getMenuAsTree("root");
        return computeAppsAndMenuItems(menuTree);
    }

    get displayedApps() {
        const { apps } = this.appsAndMenuItems;
        return apps.map(app => {
            if (app.webIconData && !app.webIconData.startsWith("data:image")) {
                const prefix = app.webIconData.startsWith("P")
                    ? "data:image/svg+xml;base64,"
                    : "data:image/png;base64,";
                app.webIconData = prefix + app.webIconData.replace(/\s/g, "");
            }
            return app;
        });
    }

    get isDarkMode() {
        return isDarkModeEnabled();
    }

    get backgroundImageStyle() {
        if (isDarkModeEnabled()) {
            return (
                "background: linear-gradient(145deg, #1a1625 0%, #2d1b35 45%, #1a0a1e 100%) !important;"
            );
        }
        return (
            "background: linear-gradient(145deg, #e7e9ed 0%, #d8dce3 50%, #e7e9ed 100%) !important;"
        );
    }

    onToggleDarkMode() {
        toggleDarkMode();
    }

    _focusInput() {
        if (this.searchInputRef.el) {
            this.searchInputRef.el.focus({ preventScroll: true });
        }
    }

    onSearchBlur() {
        if (hasTouch()) { return; }
        setTimeout(() => {
            if (document.activeElement === document.body && this.ui.activeElement === document) {
                this._focusInput();
            }
        }, 0);
    }

    onAppClicked(app) {
        this.menuService.selectMenu(app);
    }
}
