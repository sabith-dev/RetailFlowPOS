# RetailFlow POS

Modern Point-of-Sale and Billing Management System for textile/retail businesses.

## Project Description

RetailFlow POS is a full-featured POS and billing software with two portals:

- **Admin Portal** – Product, Staff, Supplier, Returns, Ledger, Reports management
- **Billing Portal** – Staff POS for product selection, payment, and invoice generation
- **Mobile Admin UI** – Complete Admin Portal in mobile-app style layout

## Features

### Admin Portal
- Dashboard with live sales stats
- Product CRUD (SKU, stock, size, color, brand, image)
- Supplier management
- Staff management (role-based: ADMIN / STAFF)
- Product return handling with stock restoration
- Financial ledger
- Sales, Inventory & Profit reports

### Billing Portal
- Product search & cart
- Discount support
- Cash / UPI / Card payment
- Automatic stock reduction
- Invoice generation & print
- Transaction history

### Mobile Admin
- Full Admin functionality in mobile layout
- Bottom navigation
- Responsive design

## Technology Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python, Django 6.x                  |
| Database  | SQLite (dev) / PostgreSQL ready     |
| Frontend  | HTML, CSS, Bootstrap 5, JavaScript  |
| Auth      | Django Authentication + Roles       |
| Other     | Pillow, python-dotenv               |


Purpose URL Login http://127.0.0.1:8000/accounts/login/
Admin Dashboard http://127.0.0.1:8000/admin/
POS Billing http://127.0.0.1:8000/billing/pos/
Mobile Admin UIhttp://127.0.0.1:8000/admin/mobile/
Products http://127.0.0.1:8000/admin/products/
Suppliers http://127.0.0.1:8000/admin/suppliers/
Staff http://127.0.0.1:8000/accounts/staff/
Returns http://127.0.0.1:8000/admin/returns/
Ledger http://127.0.0.1:8000/admin/ledger/
Reports http://127.0.0.1:8000/admin/reports/
Project Structure
textRetailFlowPOS/
├── accounts/          # Auth, Staff management
├── products/          # Product CRUD
├── suppliers/         # Supplier CRUD
├── billing/           # POS, Cart, Invoice
├── returns/           # Product returns
├── ledger/            # Financial ledger
├── reports/           # Sales, Inventory, Profit
├── dashboard/         # Admin dashboard + Mobile views
├── templates/         # HTML templates
├── static/            # CSS, JS
└── config/            # Settings, URLs
Assumptions & Notes

SQLite is used by default for easy setup. PostgreSQL config is ready in settings.py.
Soft delete (is_active) is used for Products, Suppliers, and Staff.
Invoice format: INV-YYYYMMDD-XXXX
Stock is automatically reduced on sale and increased on return.
Role-based access control: Admin has full access, Staff can only use Billing portal.
