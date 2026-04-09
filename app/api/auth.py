from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models.admin import Admin
from app.models.teacher import Teacher
from app.services.auth_service import AuthService
from app.utils.response import success_response, error_response
from app.utils.validators import validate_required
from app.utils.decorators import get_current_user_id

auth_bp = Blueprint('auth', __name__)


# ─── ĐĂNG NHẬP ───────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return error_response("Dữ liệu không hợp lệ", 400)

    errors = validate_required(data, ['username', 'password'])
    if errors:
        return error_response("Vui lòng nhập đầy đủ username và mật khẩu", 400, errors)

    try:
        token, user_dict = AuthService.login(data['username'].strip(), data['password'])
        return success_response({
            "access_token": token,
            "user": user_dict
        }, "Đăng nhập thành công")
    except ValueError as e:
        return error_response(str(e), 401)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)


# ─── ĐĂNG KÝ (Giáo viên tự đăng ký) ─────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    """Giáo viên tự đăng ký → status=pending, chờ admin duyệt"""
    data = request.get_json()
    if not data:
        return error_response("Dữ liệu không hợp lệ", 400)

    errors = validate_required(data, ['username', 'password', 'full_name'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        teacher = AuthService.register_teacher(data)
        return success_response(
            teacher.to_dict(),
            "Đăng ký thành công! Vui lòng chờ admin phê duyệt tài khoản.",
            201
        )
    except ValueError as e:
        if "được sử dụng" in str(e):
            return error_response(str(e), 409)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)


# ─── THÔNG TIN TÀI KHOẢN ─────────────────────────────────────────────────────

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    role, uid = get_current_user_id()
    try:
        if role == 'admin':
            user = Admin.query.get(uid)
        else:
            user = Teacher.query.get(uid)

        if not user:
            return error_response("Tài khoản không tồn tại", 404)
        return success_response(user.to_dict())
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)


# ─── ĐỔI MẬT KHẨU ────────────────────────────────────────────────────────────

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    data = request.get_json()
    errors = validate_required(data, ['old_password', 'new_password'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    role, uid = get_current_user_id()
    from app.extensions import db
    try:
        AuthService.change_password(role, uid, data['old_password'], data['new_password'])
        return success_response(message="Đổi mật khẩu thành công")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)