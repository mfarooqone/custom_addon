import base64
import hashlib

from odoo import api, models, tools

ADDON_ICONS = ('custom_contacts', 'custom_invoice', 'college_erp')


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.depends('icon')
    def _get_icon_image(self):
        originals = {
            module.id: module.icon
            for module in self
            if module.icon and '?' in module.icon
        }
        for module in self:
            if module.id in originals:
                module.icon = originals[module.id].split('?')[0]
        super()._get_icon_image()
        for module in self:
            if module.id in originals:
                module.icon = originals[module.id]

    @api.model
    def _refresh_module_icon_from_disk(self, module_name):
        module = self.search([('name', '=', module_name)], limit=1)
        if not module:
            return
        info = self.get_module_info(module_name)
        path = (info.get('icon') or f'/{module_name}/static/description/icon.png').split('?')[0]
        try:
            with tools.file_open(path.removeprefix('/'), 'rb', filter_ext=('.png', '.svg', '.gif', '.jpeg', '.jpg')) as f:
                token = hashlib.md5(f.read()).hexdigest()[:12]
        except OSError:
            return
        module.icon = f'{path}?v={token}'

    @api.model
    def _refresh_all_addon_icons(self):
        for name in ADDON_ICONS:
            self._refresh_module_icon_from_disk(name)
        menu = self.env.ref('college_erp.menu_college_erp_root', raise_if_not_found=False)
        if menu and menu.web_icon:
            menu.write({'web_icon': menu.web_icon})
