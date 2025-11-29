# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LANDA is a data management system for the Landesverband Sächsischer Angler e.V. (State Association of Saxon Anglers). It's built as a Frappe/ERPNext custom application for managing organizations, members, water bodies, fishing permits, sales orders, and related activities.

**Tech Stack:**
- Backend: Python 3.10+ (Frappe Framework 15.x, ERPNext 15.x)
- Frontend: JavaScript (ES6+), Vue.js
- Additional dependencies: pandas, numpy, thefuzz

## Development Commands

### Running Tests

Run all tests:
```bash
bench --site [site-name] run-tests --app landa
```

Run tests for a specific module:
```bash
bench --site [site-name] run-tests --app landa --module landa.organization_management.doctype.organization.test_organization
```

Run a specific test:
```bash
bench --site [site-name] run-tests --app landa --module landa.organization_management.doctype.organization.test_organization --test test_autoname
```

### Code Quality

Lint Python code (Ruff):
```bash
ruff check landa/
```

Auto-fix Python linting issues:
```bash
ruff check --fix landa/
```

Format Python code:
```bash
ruff format landa/
```

Lint JavaScript code (ESLint):
```bash
npx eslint landa/
```

Format JavaScript code (Prettier):
```bash
npx prettier --write "landa/**/*.js"
```

### Installation & Migration

Install the app on a site:
```bash
bench --site [site-name] install-app landa
```

Run migrations after code changes:
```bash
bench --site [site-name] migrate
```

### Custom Bench Commands

Create demo accounts for testing permissions:
```bash
bench --site [site-name] make-demo-accounts [organization-name]
```

Import water body GeoJSON data:
```bash
bench --site [site-name] import-geojson /path/to/file.geojson
```

Update organization series (internal maintenance):
```bash
bench --site [site-name] update-organization-series
```

### Development Server

Start the development server (from bench root):
```bash
bench start
```

## Architecture Overview

### Module Structure

The app is organized into functional modules:

1. **`organization_management/`** - Core member and organization management
   - Hierarchical organization structure (State → Regional → Local → Groups)
   - LANDA Members with automatic naming based on organization hierarchy
   - Member Functions and Categories for role-based permissions
   - Awards, External Contacts, Data Import

2. **`landa_sales/`** - Sales and billing functionality
   - Customized Sales Orders, Sales Invoices, Payment Entries
   - Statement of Fees and Payments
   - Payment reconciliation and party handling
   - Multiple print formats for invoices and statements

3. **`landa_stock/`** - Inventory and delivery management
   - Customized Delivery Notes and Items
   - Item variants for fishing permits (Erlaubnisscheinart, Gültigkeitsjahr, etc.)
   - Issuing statistics and member count reports

4. **`water_body_management/`** - Water body and fishing data
   - Water Bodies with GeoJSON location data
   - Fish Species with images and regulations
   - Catch log entries
   - Stocking targets and lease management
   - Change log tracking for API consumers
   - Firebase integration for mobile app notifications

5. **`overrides/`** - Core Frappe/ERPNext customizations
   - Address and Contact modifications
   - User management with organization linkage
   - E-Invoice import customization

### Key Concepts

#### Organization Hierarchy
Organizations form a tree structure with automatic naming:
- **Level 0**: State Organization (e.g., "LV") - Creates an ERPNext Company
- **Level 1**: Regional Organization (e.g., "AVL", "AVS") - Creates an ERPNext Company
- **Level 2**: Local Organization (e.g., "AVL-001") - Creates an ERPNext Customer
- **Level 3**: Local Group (e.g., "AVL-002-01") - Creates an ERPNext Customer
- **Members**: Belong to leaf organizations (e.g., "AVL-001-0001")

**ERPNext Integration:**
- Level 0 and Level 1 organizations function as ERPNext Companies for accounting purposes
- Level 2 and Level 3 organizations function as ERPNext Customers belonging to their Level 1 parent Company
- Level 0 (State Organization) primarily uses ERPNext for parsing e-invoices and invoicing external advertising customers
- Level 1 (Regional Organizations) handle the main accounting operations for their member organizations, including selling supplies (fishing permits, equipment) through the standard ERPNext sales cycle: Sales Order → Delivery Note → Sales Invoice → Payment Entry

#### Permissions System
- Users are restricted by default to their own Organization and LANDA Member via User Permissions
- Member Functions assign categories that grant additional roles and expanded access
- Member Function Categories define organization level access and whether users can view/edit other members' data
- Multiple active Member Functions grant the union of all permissions
- Tag permissions are scoped to organizations using a custom Tag Organization child table

#### Deletion Behavior
Deleting a LANDA Member:
- Attempts to delete linked User (or disables it if deletion fails)
- Deletes Addresses/Contacts linked only to this member
- Decrements naming series if member was just created
- Removes/unsets all links in child tables and optional link fields
- Deletes documents with mandatory links to this member

#### Document Event Hooks
The app extensively uses Frappe's document event hooks (`doc_events` in hooks.py) to:
- Customize autoname behavior for core doctypes (Sales Order, Delivery Note, etc.)
- Add validation logic before/during document save
- Trigger actions on submit (e.g., delivery note submission)
- Manage version logs and Firebase notifications for water body changes
- Synchronize permissions when Member Functions are updated

### API Layer

Public API endpoints (`landa/api.py`) for external applications (e.g., Angelatlas mobile app):
- `GET /api/method/landa.api.organization` - List organizations
- `GET /api/method/landa.api.water_body` - List water bodies with fish species and GeoJSON
- `GET /api/method/landa.api.fish_species` - Fish species data
- `GET /api/method/landa.api.legal` - Water body rules, privacy policy, imprint
- `GET /api/method/landa.api.change_log` - Track changes since a given datetime
- `GET /api/method/landa.api.custom_icon` - Custom icons for map display

See `docs/api.md` for detailed API documentation.

### Frontend Customization

Client-side scripts are organized by doctype:
- `doctype_js` in hooks.py maps doctypes to their JS files
- `doctype_list_js` customizes list views
- Custom controllers in `landa/public/js/controllers/`
- Frappe global variables and utilities are available (see `eslint.config.mjs` for full list)

### Testing Patterns

Tests follow Frappe conventions:
- Use `frappe.tests.utils.FrappeTestCase` as base class
- Test files named `test_*.py` in same directory as module
- Tests should work with demo fixtures (created via `make-demo-accounts`)
- Common pattern: `frappe.get_all()`, `frappe.db.exists()`, assertions on expected data

## Important Files

- `landa/hooks.py` - Central configuration: fixtures, scheduled tasks, doc events, overrides
- `landa/install.py` - Post-install setup scripts
- `landa/migrate.py` - Migration logic (runs after every `bench migrate`)
- `landa/permissions.py` - Custom permission query logic
- `landa/commands/__init__.py` - Custom bench CLI commands
- `landa/api.py` - Public API endpoints for external apps
- `pyproject.toml` - Python dependencies and Ruff configuration
- `.pre-commit-config.yaml` - Pre-commit hooks for code quality
- `eslint.config.mjs` - ESLint configuration with Frappe globals

## Translation

Translations are managed using PO files in the `locale/` directory. The recent migration moved translations from CSV to PO format (see commit 9f019d2).

## Pre-commit Hooks

The project uses pre-commit hooks for automated code quality:
- Ruff linting and formatting for Python
- Prettier for JavaScript/Vue/SCSS
- Trailing whitespace, YAML/JSON validation
- Configured via `.pre-commit-config.yaml`

Install hooks:
```bash
pre-commit install
```

## CORS Configuration

For API access from Angelatlas web apps, CORS must be configured in `sites/common_site_config.json`:
```json
{
  "allow_cors": [
    "https://angelatlas.devid.net",
    "https://www.angelatlas-sachsen.de",
    "https://angelatlas-sachsen.de"
  ]
}
```

Also requires nginx configuration changes (see `docs/installation.md`).

## Version

The app targets Frappe 15.x and ERPNext 15.x (branch: version-15-hotfix).
