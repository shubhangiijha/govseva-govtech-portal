🌐 GovSeva — Citizen Grievance & Service Portal

GovSeva is a GovTech demo project built to simulate how public service grievance portals work.
It implements ticketing, SLA tracking, dashboards, and audit logs with role-based access.

✨ Features

👤 User Roles: Citizen, Officer, Admin

📝 Ticket Management: Citizens create issues, Officers/Admins assign & resolve

⏱ SLA Deadlines: 24h / 48h / 72h response times based on priority

📊 Analytics Dashboard: KPIs (Open / In-Progress / Resolved / Closed) + category reports

🗂 Audit Logs: Every action (create, assign, update status, comment) is recorded

🛠 SDLC Flow: Requirement gathering → Design (ERD) → Coding → Testing → Deployment

🔧 Tech Stack

Backend: Python (Flask), SQLAlchemy

Database: SQLite (default), compatible with MySQL/PostgreSQL

Frontend: HTML, CSS, Bootstrap, JavaScript

Other Tools: Flask-Login, Flask-WTF, Docker, Gunicorn

🚀 Quick Start
# 1) Clone repo
git clone https://github.com/shubhangijiha/govseva-govtech-portal.git
cd govseva-govtech-portal

# 2) Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # (Windows)

# 3) Install dependencies
pip install -r requirements.txt

# 4) Initialize DB (with seed users)
flask init-db

# 5) Run
python app.py
# Open http://localhost:5000

👩‍💻 Demo Logins (Seeded Users)

Admin: admin@govseva.local / admin123

Officer (Sanitation): officer1@govseva.local / officer123

Officer (Water): officer2@govseva.local / officer123

Citizen: citizen@govseva.local / citizen123

📄 Resume

📊 ERD (Mermaid)
erDiagram
  USER ||--o{ TICKET : "citizen_id"
  USER ||--o{ TICKET : "assigned_to_id"
  USER ||--o{ COMMENT : "user_id"
  DEPARTMENT ||--o{ USER : "has"
  DEPARTMENT ||--o{ TICKET : "manages"
  TICKET ||--o{ COMMENT : "has"
  USER ||--o{ AUDITLOG : "user_id"

  USER {
    int id PK
    string name
    string email
    string password_hash
    string role
    int department_id FK
  }
  DEPARTMENT {
    int id PK
    string name
  }
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
  COMMENT {
    int id PK
    int ticket_id FK
    int user_id FK
    text body
    datetime created_at
  }
  AUDITLOG {
    int id PK
    int user_id FK
    string action
    string resource_type
    int resource_id
    text meta_json
    datetime created_at
  }

🏆 Why This Project Matters

Mirrors GovTech Analyst JD: SQL, Python, SDLC, requirement analysis, troubleshooting

Demonstrates real public sector workflows (ticketing, audit, SLA)

Deployable on Render/Railway/Fly.io with Docker support
