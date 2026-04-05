from flask import Blueprint

from app.api.auth import auth_bp
from app.api.teacher import teacher_bp
from app.api.admin import admin_bp

__all__ = ['auth_bp', 'teacher_bp', 'admin_bp']
