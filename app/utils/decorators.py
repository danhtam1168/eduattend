from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.utils.response import error_response


def admin_required(fn):
    """Decorator: chỉ cho phép admin truy cập"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return error_response("Chỉ admin mới có quyền truy cập", 403)
        if not user.is_active:
            return error_response("Tài khoản đã bị khoá", 401)
        return fn(*args, **kwargs)
    return wrapper


def teacher_required(fn):
    """Decorator: chỉ cho phép user đang active (teacher hoặc admin)"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return error_response("Tài khoản không tồn tại hoặc đã bị khoá", 401)
        return fn(*args, **kwargs)
    return wrapper
