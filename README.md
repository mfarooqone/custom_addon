# Odoo 19 Custom Addons

Collection of custom Odoo 19 Enterprise modules by **Najoom Al Thuraya**.

## Modules

| Module | Description |
|--------|-------------|
| `college_erp` | College student management (admissions, records) |
| `custom_contacts` | Typed contacts with auto-generated customer, vendor, and employee IDs |
| `custom_invoice` | Custom invoice PDF layout, fields, and company toggle |
| `crm_integration` | CRM REST APIs, API key settings, and static API documentation |

## Requirements

- Odoo 19.0 (Enterprise)
- Python 3.10 – 3.13
- PostgreSQL 14+

## Installation

1. Clone this repository into your addons path:

```bash
git clone https://github.com/mfarooqone/custom_addon.git /path/to/odoo/custom_addon
```

2. Add the path to `odoo.conf`:

```ini
addons_path = /path/to/odoo/addons,/path/to/odoo/enterprise,/path/to/odoo/custom_addon
```

3. Restart Odoo, update the Apps list, and install the modules you need.

**Suggested install order** (if using all Najoom modules):

```bash
./odoo-bin -c odoo.conf -d YOUR_DB -i custom_contacts,custom_invoice,college_erp --stop-after-init
```

## Author

**Najoom Al Thuraya** — [althurayauae.com](https://althurayauae.com/)

## License

LGPL-3 — see [LICENSE](LICENSE).
