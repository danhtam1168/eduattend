from flask import Flask
from flask_cors import CORS
from app.config import config
from app.extensions import db, migrate, jwt, bcrypt


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Cấu hình CORS cho frontend Vite
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        from app.models import (
            Admin, Teacher, Student, Subject, Room, Class,
            StudentClass, Schedule, TeacherAttendance, StudentAttendance,
            MonthlyFee, Payment, TeacherSalary, SystemConfig, ActivityLog,
            ClassSchedule
        )

    # ── Auth ──────────────────────────────────────────────────────────────────
    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # ── Admin ─────────────────────────────────────────────────────────────────
    from app.api.admin.dashboard import dashboard_bp
    from app.api.admin.teachers import teachers_bp
    from app.api.admin.students import students_bp
    from app.api.admin.subjects import subjects_bp
    from app.api.admin.rooms import rooms_bp
    from app.api.admin.classes import classes_bp
    from app.api.admin.schedules import schedules_bp
    from app.api.admin.class_schedules import class_schedules_bp
    from app.api.admin.teacher_attendances import teacher_attendances_bp
    from app.api.admin.monthly_fees import monthly_fees_bp
    from app.api.admin.payments import payments_bp
    from app.api.admin.teacher_salaries import teacher_salaries_bp

    app.register_blueprint(dashboard_bp,           url_prefix='/api/admin/dashboard')
    app.register_blueprint(teachers_bp,            url_prefix='/api/admin/teachers')
    app.register_blueprint(students_bp,            url_prefix='/api/admin/students')
    app.register_blueprint(subjects_bp,            url_prefix='/api/admin/subjects')
    app.register_blueprint(rooms_bp,               url_prefix='/api/admin/rooms')
    app.register_blueprint(classes_bp,             url_prefix='/api/admin/classes')
    app.register_blueprint(schedules_bp,           url_prefix='/api/admin/schedules')
    app.register_blueprint(class_schedules_bp,     url_prefix='/api/admin/class-schedules')
    app.register_blueprint(teacher_attendances_bp, url_prefix='/api/admin/teacher-attendances')
    app.register_blueprint(monthly_fees_bp,        url_prefix='/api/admin/monthly-fees')
    app.register_blueprint(payments_bp,            url_prefix='/api/admin/payments')
    app.register_blueprint(teacher_salaries_bp,    url_prefix='/api/admin/teacher-salaries')

    # ── Teacher ───────────────────────────────────────────────────────────────
    from app.api.teacher.sessions import teacher_sessions_bp
    from app.api.teacher.attendance import teacher_attendance_bp
    from app.api.teacher.profile import teacher_profile_bp

    app.register_blueprint(teacher_sessions_bp,   url_prefix='/api/teacher')
    app.register_blueprint(teacher_attendance_bp,  url_prefix='/api/teacher')
    app.register_blueprint(teacher_profile_bp,     url_prefix='/api/teacher')

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route('/api/health')
    def health():
        return {"status": "ok", "version": "2.0", "message": "EduAttend API v2 is running"}, 200

    return app