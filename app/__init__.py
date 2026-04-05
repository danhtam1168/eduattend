from flask import Flask
from app.config import config
from app.extensions import db, migrate, jwt, bcrypt


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        from app.models import User, SalaryRate, TeachingSession, Student, StudentAttendance

    # Đăng ký Blueprints
    from app.api.auth import auth_bp
    from app.api.teacher import teacher_bp
    from app.api.admin import admin_bp

    app.register_blueprint(auth_bp,    url_prefix='/api/auth')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(admin_bp,   url_prefix='/api/admin')

    # Health check
    @app.route('/api/health')
    def health():
        return {"status": "ok", "message": "TeachTrack API is running"}, 200

    return app