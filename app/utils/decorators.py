from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.models.admin import Admin
from app.models.teacher import Teacher
from app.utils.response import error_response


def _parse_identity(identity: str):
    """
    Parse JWT identity string: "admin:1" → ("admin", 1) | "teacher:5" → ("teacher", 5)
    """
    try:
        role, id_str = identity.split(':', 1)
        return role, int(id_str)
    except (ValueError, AttributeError):
        return None, None


def admin_required(fn):
    """Decorator: chỉ cho phép admin truy cập"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        role, uid = _parse_identity(identity)

        if role != 'admin':
            return error_response("Chỉ admin mới có quyền truy cập", 403)

        admin = Admin.query.get(uid)
        if not admin or not admin.is_active:
            return error_response("Tài khoản không tồn tại hoặc đã bị khoá", 401)

        return fn(*args, **kwargs)
    return wrapper


def teacher_required(fn):
    """Decorator: chỉ cho phép teacher (đã active) truy cập"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        role, uid = _parse_identity(identity)

        if role not in ('teacher', 'admin'):
            return error_response("Không có quyền truy cập", 403)

        if role == 'teacher':
            teacher = Teacher.query.get(uid)
            if not teacher or teacher.status != 'active' or not teacher.is_active:
                return error_response("Tài khoản không tồn tại, chưa được duyệt hoặc đã bị khoá", 401)

        return fn(*args, **kwargs)
    return wrapper


def get_current_admin():
    """Lấy Admin object từ JWT identity hiện tại"""
    identity = get_jwt_identity()
    role, uid = _parse_identity(identity)
    if role == 'admin':
        return Admin.query.get(uid)
    return None


def get_current_teacher():
    """Lấy Teacher object từ JWT identity hiện tại"""
    identity = get_jwt_identity()
    role, uid = _parse_identity(identity)
    if role == 'teacher':
        return Teacher.query.get(uid)
    return None


def get_current_user_id():
    """Trả về (role, id) từ JWT identity hiện tại"""
    identity = get_jwt_identity()
    return _parse_identity(identity)
