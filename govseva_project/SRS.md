# Software Requirements Specification (SRS) — GovSeva

## 1. Purpose
Provide a simple, auditable citizen grievance & service request portal suited for public-sector workflows.

## 2. Users & Roles
- **Citizen**: Registers, submits requests, tracks status, comments.
- **Officer**: Views/assigns/updates tickets for their department, comments.
- **Admin**: Global oversight, can assign tickets to officers, monitors KPIs.

## 3. Functional Requirements
- User registration/login with role-based access.
- Create ticket with title, description, category, priority.
- Calculate due date per SLA (24/48/72 hours).
- Officer/Admin dashboard: Open/In-Progress/Resolved/Closed counts; tickets by category.
- Comments on tickets.
- Audit log for create/assign/status change/comment events.

## 4. Non-Functional Requirements
- Security: password hashing (bcrypt), authenticated routes.
- Performance: handle 100 concurrent users (scalable with WSGI / Gunicorn).
- Reliability: SQLite by default; port to MySQL/PostgreSQL.
- Usability: Bootstrap UI, minimal clicks for core flows.

## 5. Data Model
See ERD in README.md (Mermaid).

## 6. Constraints & Assumptions
- No file uploads/email in MVP; can be added later.
- Department mapping is static for MVP.

## 7. Acceptance Criteria
- Citizen can register, login, create a ticket, view it.
- Officer can update ticket status.
- Admin sees KPIs on dashboard.
- Audit logs populate for key actions.
