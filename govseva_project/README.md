# GovSeva — Citizen Grievance & Service Request Portal

**Why this project for KPMG GovTech?**  
- Mirrors JD-1 requirements: SDLC participation, coding in **Python**, **SQL** with **relational schema**, documentation, and troubleshooting.  
- Demonstrates **role-based access**, **SLA due dates**, **audit logs**, and an **operations dashboard** — all common in public-sector (GovTech) engagements.  

## Features
- Roles: **Citizen**, **Officer**, **Admin**
- Citizen: register/login, **create tickets**, view status, comment
- Officer/Admin: **dashboard KPIs**, list tickets by status/category, **update status**, **assign** tickets
- **SLA** due-times by priority (24/48/72h)
- **Audit logs** for key actions (create/assign/status change/comment)
- **Relational schema** with SQLAlchemy (SQLite by default; easy to switch to MySQL/PostgreSQL)
- Seed data (admin/officers/citizen demo users)

## Tech Stack
- Python 3.10+ / Flask, Flask-Login, Flask-WTF, SQLAlchemy
- SQLite (default) → can switch to MySQL/PostgreSQL via `DATABASE_URL`
- Bootstrap UI

## Quick Start (Windows friendly)
```bash
# 1) Create venv (Python 3.12 installed at C:\Program Files\Python312 per your setup)
python -m venv .venv
.venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Initialize DB with seed data
set FLASK_APP=app.py
flask init-db

# 4) Run
python app.py
# open http://localhost:5000
```

**Demo logins (from seed):**
- Admin: `admin@govseva.local` / `admin123`
- Officer (Sanitation): `officer1@govseva.local` / `officer123`
- Officer (Water): `officer2@govseva.local` / `officer123`
- Citizen: `citizen@govseva.local` / `citizen123`

## Switch to MySQL (optional)
Set `DATABASE_URL` in `.env` (copy from `.env.example`) to:  
```
mysql+pymysql://user:password@localhost:3306/govseva
```
Install `PyMySQL` as needed: `pip install PyMySQL`.

## ERD (Mermaid)
```mermaid
erDiagram
  USER ||--o{ TICKET : "citizen_id"
  USER ||--o{ TICKET : "assigned_to_id"
  USER ||--o{ COMMENT : "user_id"
  DEPARTMENT ||--o{ USER : ""
  DEPARTMENT ||--o{ TICKET : ""
  TICKET ||--o{ COMMENT : ""
  USER ||--o{ AUDITLOG : "user_id"

  USER {
    int id PK
    string name
    string email
    bytes password_hash
    string role
    int department_id FK
  }
  DEPARTMENT { int id PK, string name }
  TICKET {
    int id PK
    string title
    text description
    string category
    string status
    string priority
    int citizen_id FK
    int assigned_to_id FK
    int department_id FK
    datetime created_at
    datetime updated_at
    datetime due_at
  }
  COMMENT { int id PK, int ticket_id FK, int user_id FK, text body, datetime created_at }
  AUDITLOG { int id PK, int user_id FK, string action, string resource_type, int resource_id, text meta_json, datetime created_at }
```

## API (selected)
- `POST /login`, `POST /register`
- `GET /ticket/<id>`, `POST /ticket/new`
- `POST /status/<ticket_id>` → body: `status=OPEN|IN_PROGRESS|RESOLVED|CLOSED`
- `POST /assign/<ticket_id>/<officer_id>`

## Testing
```bash
pytest -q
```

## Interview Talking Points
- How you applied **SDLC**: requirement gathering → design (ERD, routes) → implementation → testing → deployment options (Docker/MySQL)
- **Role-based access**, **SLA logic**, and **auditability** (critical in GovTech)
- How to extend: file uploads, service-level breach alerts, email notifications, analytics with OAC/PowerBI
```

