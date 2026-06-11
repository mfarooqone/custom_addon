# Odoo 19 College ERP

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo](https://img.shields.io/badge/Odoo-19.0-875A7B.svg)](https://www.odoo.com)
[![Version](https://img.shields.io/badge/version-19.0.1.0.2-green.svg)](https://github.com/mfarooqone/college_erp)

**Odoo 19 Community addon** for college and institute management — student records, admissions, and education workflows.

Repository: [github.com/mfarooqone/college_erp](https://github.com/mfarooqone/college_erp)

---

## Features

- **Student registry** — Name, admission number, admission date, gender, contact details, and address
- **Dedicated app** — *College ERP* on the Odoo home screen with app icon
- **List & form views** — Browse and manage students from the backend
- **Access rights** — Separate **User** and **Administrator** security groups
- Built for **Odoo 19 Community Edition**

## Screenshots

_Add screenshots of the Students list and form views here._

---

## Requirements

| Component | Version |
|-----------|---------|
| Odoo | 19.0 (Community) |
| Python | 3.10 – 3.13 |
| PostgreSQL | 14+ |

---

## Installation

### 1. Clone into your addons directory

Clone this repository so the folder name matches the technical module name `college_erp`:

```bash
cd /path/to/your/odoo/custom_addon
git clone https://github.com/mfarooqone/college_erp.git college_erp
```

### 2. Add the addons path in `odoo.conf`

Ensure the **parent** directory of the module is on `addons_path`:

```ini
addons_path = /path/to/odoo/addons,/path/to/odoo/custom_addon
```

Expected layout:

```text
custom_addon/
└── college_erp/                    ← Git repo + Odoo module root
    ├── __init__.py
    ├── __manifest__.py
    ├── README.md
    ├── .gitignore
    ├── models/
    ├── security/
    ├── static/description/icon.png
    └── views/
```

### 3. Install the module

**From the UI**

1. Restart Odoo
2. Enable **Developer mode** (*Settings → Activate the developer mode*)
3. Go to **Apps → Update Apps List**
4. Search **College ERP** → **Install**

**From the command line**

```bash
./odoo-bin -c odoo.conf -d YOUR_DATABASE -i college_erp --stop-after-init
```

**Upgrade** after pulling changes:

```bash
./odoo-bin -c odoo.conf -d YOUR_DATABASE -u college_erp --stop-after-init
```

### 4. Assign user access

After install, give users access to the app:

1. **Settings → Users** → open the user
2. Under **College ERP**, enable **User** or **Administrator**
3. Save

| Group | Permissions |
|-------|-------------|
| **User** | Read, create, edit students (no delete) |
| **Administrator** | Full access including delete (assigned to admin by default) |

Without one of these groups, users will not see the **College ERP** app or student records.

### 5. Open the app

Go to **College ERP → Students Management → Students** and create your first student.

---

## Configuration

No extra system settings are required beyond user group assignment (see above).

### Custom app icon

Replace the default icon with your own branding:

```text
college_erp/static/description/icon.png
```

Use a square PNG (recommended ~256×256), then upgrade the module:

```bash
./odoo-bin -c odoo.conf -d YOUR_DATABASE -u college_erp --stop-after-init
```

The root menu uses `web_icon="college_erp,static/description/icon.png"` in `views/college_erp_menus.xml`.

---

## Development

This folder is both the Odoo module and the Git repository root:

```bash
cd /path/to/custom_addon/college_erp
# edit models, views, security, manifest...
git add .
git commit -m "feat: your change"
git push origin main
```

Do not commit `__pycache__`, virtualenvs, or secrets (see `.gitignore`).

After code changes, upgrade the module on your database (`-u college_erp`) and restart Odoo.

---

## Module structure

| Item | Value |
|------|--------|
| Technical name | `college_erp` |
| Version | `19.0.1.0.2` |
| Main model | `college.students` |
| Window action | `action_college_students` |
| Depends on | `base` |
| License | LGPL-3 |

```text
college_erp/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── college_students.py
├── security/
│   ├── college_erp_security.xml    # groups & privileges
│   └── ir.model.access.csv         # model access rules
├── static/
│   └── description/
│       └── icon.png                # app icon
└── views/
    ├── college_students_views.xml  # list, form, action
    └── college_erp_menus.xml       # app & menu items
```

### Student fields (`college.students`)

| Field | Type | Notes |
|-------|------|--------|
| `name` | Char | Required |
| `admission_number` | Char | Required |
| `admission_date` | Date | Required |
| `gender` | Selection | Male / Female |
| `email` | Char | |
| `phone` | Char | |
| `age` | Integer | |
| `address` | Text | |

### Security groups

| XML ID | Name |
|--------|------|
| `college_erp.group_college_erp_user` | College ERP / User |
| `college_erp.group_college_erp_manager` | College ERP / Administrator |

---

## Troubleshooting

### Blank Odoo screen or `load_menus` 404

Usually caused by a menu pointing at a deleted window action after a module upgrade.

1. Upgrade the module: `-u college_erp`
2. Restart Odoo
3. Clear browser **Local Storage** keys `webclient_menus` and `webclient_menus_version`, then hard-refresh

### Broken app icon on home screen

Ensure `static/description/icon.png` exists and the module was upgraded after adding it. Hard-refresh the browser if the old broken image is cached.

---

## Roadmap

- [ ] Courses and programs
- [ ] Departments and faculty
- [ ] Fees and invoicing
- [ ] Attendance and timetables
- [ ] Reports and certificates

---

## Contributing

1. Fork [college_erp](https://github.com/mfarooqone/college_erp)
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "feat: add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## Author

**Najoom Al Thuraya**  
Website: [althurayauae.com](https://althurayauae.com/)

Maintainer: [@mfarooqone](https://github.com/mfarooqone)

---

## License

This project is licensed under the [GNU Lesser General Public License v3.0](https://www.gnu.org/licenses/lgpl-3.0.html) (LGPL-3), same as Odoo Community Edition.
