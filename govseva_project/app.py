from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Department, Ticket, Comment, AuditLog, set_due, Role, TicketStatus
from forms import RegisterForm, LoginForm, TicketForm
from config import Config
from sqlalchemy import func
import json

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.cli.command("init-db")
    def init_db():
        with app.app_context():
            db.drop_all()
            db.create_all()

            # Seed departments
            d1 = Department(name="Sanitation")
            d2 = Department(name="Water Supply")
            d3 = Department(name="Electricity")
            d4 = Department(name="Roads")
            db.session.add_all([d1,d2,d3,d4])

            # Seed users
            admin = User(name="Admin", email="admin@govseva.local", role=Role.ADMIN, department=d1)
            admin.set_password("admin123")
            off1 = User(name="Officer Sanitation", email="officer1@govseva.local", role=Role.OFFICER, department=d1)
            off1.set_password("officer123")
            off2 = User(name="Officer Water", email="officer2@govseva.local", role=Role.OFFICER, department=d2)
            off2.set_password("officer123")
            citizen = User(name="Shubhangi", email="citizen@govseva.local", role=Role.CITIZEN)
            citizen.set_password("citizen123")
            db.session.add_all([admin, off1, off2, citizen])
            db.session.commit()
            print("Database initialized with seed data.")

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role in (Role.OFFICER, Role.ADMIN):
                # Officer/Admin dashboard
                open_count = Ticket.query.filter(Ticket.status==TicketStatus.OPEN).count()
                inprog_count = Ticket.query.filter(Ticket.status==TicketStatus.IN_PROGRESS).count()
                resolved_count = Ticket.query.filter(Ticket.status==TicketStatus.RESOLVED).count()
                closed_count = Ticket.query.filter(Ticket.status==TicketStatus.CLOSED).count()
                by_category = db.session.query(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category).all()
                return render_template("dashboard.html",
                    open_count=open_count, inprog_count=inprog_count,
                    resolved_count=resolved_count, closed_count=closed_count,
                    by_category=by_category)
            else:
                # Citizen home - list my tickets
                my_tickets = Ticket.query.filter_by(citizen_id=current_user.id).order_by(Ticket.created_at.desc()).all()
                return render_template("citizen_home.html", tickets=my_tickets)
        return render_template("index.html")

    @app.route("/register", methods=["GET","POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data.lower()).first():
                flash("Email already registered", "warning")
                return redirect(url_for("register"))
            u = User(name=form.name.data.strip(), email=form.email.data.lower(), role=Role.CITIZEN)
            u.set_password(form.password.data)
            db.session.add(u); db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET","POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = LoginForm()
        if form.validate_on_submit():
            u = User.query.filter_by(email=form.email.data.lower()).first()
            if u and u.check_password(form.password.data):
                login_user(u)
                return redirect(url_for("index"))
            flash("Invalid credentials", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/ticket/new", methods=["GET","POST"])
    @login_required
    def new_ticket():
        if current_user.role != Role.CITIZEN:
            abort(403)
        form = TicketForm()
        if form.validate_on_submit():
            t = Ticket(
                title=form.title.data.strip(),
                description=form.description.data.strip(),
                category=form.category.data,
                status=TicketStatus.OPEN,
                priority=form.priority.data,
                citizen_id=current_user.id,
            )
            # Map category to department
            dept_map = {
                "SANITATION":"Sanitation",
                "WATER":"Water Supply",
                "ELECTRICITY":"Electricity",
                "ROADS":"Roads",
                "OTHER":"Sanitation",
            }
            dept_name = dept_map.get(form.category.data, "Sanitation")
            t.department = Department.query.filter_by(name=dept_name).first()
            set_due(t, 48 if t.priority=="MEDIUM" else (24 if t.priority=="HIGH" else 72))
            db.session.add(t); db.session.commit()
            log = AuditLog(user_id=current_user.id, action="CREATE_TICKET", resource_type="TICKET", resource_id=t.id,
                           meta_json=json.dumps({"title": t.title, "priority": t.priority}))
            db.session.add(log); db.session.commit()
            flash("Ticket submitted successfully", "success")
            return redirect(url_for("index"))
        return render_template("ticket_new.html", form=form)

    @app.route("/ticket/<int:ticket_id>", methods=["GET","POST"])
    @login_required
    def ticket_detail(ticket_id):
        t = Ticket.query.get_or_404(ticket_id)
        if current_user.role == Role.CITIZEN and t.citizen_id != current_user.id:
            abort(403)
        if request.method == "POST":
            body = request.form.get("body", "").strip()
            if body:
                c = Comment(ticket_id=t.id, user_id=current_user.id, body=body)
                db.session.add(c)
                db.session.add(AuditLog(user_id=current_user.id, action="ADD_COMMENT", resource_type="TICKET",
                                        resource_id=t.id, meta_json=json.dumps({"body": body[:120]})))
                db.session.commit()
                flash("Comment added", "success")
        return render_template("ticket_detail.html", t=t)

    @app.route("/assign/<int:ticket_id>/<int:officer_id>", methods=["POST"])
    @login_required
    def assign_ticket(ticket_id, officer_id):
        if current_user.role not in (Role.ADMIN, Role.OFFICER):
            abort(403)
        t = Ticket.query.get_or_404(ticket_id)
        officer = User.query.get_or_404(officer_id)
        if officer.role != Role.OFFICER:
            abort(400)
        t.assigned_to_id = officer.id
        db.session.add(AuditLog(user_id=current_user.id, action="ASSIGN_TICKET", resource_type="TICKET",
                                resource_id=t.id, meta_json=json.dumps({"assignee": officer.email})))
        db.session.commit()
        flash("Ticket assigned", "success")
        return redirect(url_for("index"))

    @app.route("/status/<int:ticket_id>", methods=["POST"])
    @login_required
    def update_status(ticket_id):
        t = Ticket.query.get_or_404(ticket_id)
        if current_user.role not in (Role.ADMIN, Role.OFFICER):
            abort(403)
        new_status = request.form.get("status")
        if new_status not in [s.value for s in TicketStatus]:
            abort(400)
        t.status = new_status
        db.session.add(AuditLog(user_id=current_user.id, action="UPDATE_STATUS", resource_type="TICKET",
                                resource_id=t.id, meta_json=json.dumps({"status": new_status})))
        db.session.commit()
        flash("Status updated", "success")
        return redirect(url_for("index"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
