# Mini Ledger API

A Django REST API for customer and ledger management with JWT authentication and user-scoped data access.

This project provides:
- User registration and login using JWT authentication
- Customer management (CRUD)
- Ledger entries (credit / debit) per customer
- Filtering ledger entries by date range and type
- Customer financial summary (total credit, total debit, balance)
- Strong data isolation between users

---

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- JWT Authentication (SimpleJWT)
- SQLite (for simplicity)

---

## Features Overview

### Authentication
- User registration
- User login with JWT
- Token refresh

### Customers
- Create customer
- List customers (only for logged-in user)
- Update customer
- Delete customer

### Ledger Entries
Each ledger entry contains:
- `type` (credit / debit)
- `amount`
- `note`
- `entry_date`

Features:
- Create ledger entry for a customer
- List all entries (user-scoped)
- List entries by customer
- Filter entries by:
  - date range
  - entry type (credit / debit)

### Customer Summary
For each customer:
- `total_credit`
- `total_debit`
- `balance = total_credit - total_debit`

---

## Security Notes

- Django `SECRET_KEY` is **not committed** to the repository
- Secrets are loaded from environment variables
- Each user can only access their own customers and ledger entries

---

## Project Setup (Local)

### 1) Clone the repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd mini-ledger-api
```

### 2) Create and activate virtual environment

**Windows (PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4) Environment variables

Create a `.env` file in the project root (same level as `manage.py`):

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
```

> Note: `.env` is ignored by Git and must be created manually.

---

### 5) Apply database migrations

```bash
python manage.py migrate
```

---

### 6) Run the server

```bash
python manage.py runserver
```

Server will be available at:
```
http://127.0.0.1:8000
```

---

## API Usage (Postman)

### Authentication

#### Register
**POST** `/api/auth/register/`

```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

#### Login
**POST** `/api/auth/login/`

```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

Response includes:
- `access`
- `refresh`

Use the `access` token as:
```
Authorization: Bearer <ACCESS_TOKEN>
```

---

### Customers

#### Create customer
**POST** `/api/customers/`

```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "phone": "0123456789"
}
```

#### List customers
**GET** `/api/customers/`

---

### Ledger Entries

#### Create entry
**POST** `/api/entries/`

```json
{
  "customer_id": 1,
  "entry_type": "credit",
  "amount": "100.00",
  "note": "Initial payment",
  "date": "2026-02-01"
}
```

#### List all entries
**GET** `/api/entries/`

#### List entries by customer
**GET** `/api/customers/<customer_id>/entries/`

---

### Filters

Filter by type:
```
/api/entries/?type=credit
```

Filter by date range:
```
/api/entries/?start_date=2026-02-01&end_date=2026-02-08
```

Combine filters:
```
/api/entries/?type=debit&start_date=2026-02-01&end_date=2026-02-08
```

---

### Customer Summary

**GET** `/api/customers/<customer_id>/summary/`

Example response:
```json
{
  "total_credit": "575.00",
  "total_debit": "120.00",
  "balance": "455.00"
}
```

---

## Data Isolation

- Users can only access their own customers
- Users can only access their own ledger entries
- Attempting to access another user's data returns `404`

---

## Notes

- SQLite is used for simplicity
- Project structure and API design follow standard Django REST practices
- Focus was on clarity, correctness, and security

---
