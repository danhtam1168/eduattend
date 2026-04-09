from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required

from app.extensions import db
from app.models.admin import Admin
from app.models.teacher import Teacher
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

    username = data['username'].strip()
    password = data['password']

    # Tìm trong admins trước
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        if not admin.check_password(password):
            return error_response("Tên đăng nhập hoặc mật khẩu không đúng", 401)
        if not admin.is_active:
            return error_response("Tài khoản đã bị khoá", 401)
        token = create_access_token(identity=f"admin:{admin.id}")
        return success_response({
            "access_token": token,
            "user": admin.to_dict()
        }, "Đăng nhập thành công")

    # Tìm trong teachers
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher:
        if not teacher.check_password(password):
            return error_response("Tên đăng nhập hoặc mật khẩu không đúng", 401)
        if teacher.status == 'pending':
            return error_response("Tài khoản đang chờ admin phê duyệt", 403)
        if teacher.status == 'rejected':
            return error_response("Tài khoản đã bị từ chối", 403)
        if teacher.status in ('inactive', 'on_leave') or not teacher.is_active:
            return error_response("Tài khoản đã bị khoá hoặc tạm nghỉ", 401)
        token = create_access_token(identity=f"teacher:{teacher.id}")
        return success_response({
            "access_token": token,
            "user": teacher.to_dict()
        }, "Đăng nhập thành công")

    return error_response("Tên đăng nhập hoặc mật khẩu không đúng", 401)


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

    username = data['username'].strip()

    # Kiểm tra username đã tồn tại
    if Teacher.query.filter_by(username=username).first():
        return error_response("Username đã được sử dụng", 409)
    if Admin.query.filter_by(username=username).first():
        return error_response("Username đã được sử dụng", 409)

    if len(data['password']) < 6:
        return error_response("Mật khẩu phải có ít nhất 6 ký tự", 400)

    teacher = Teacher(
        username=username,
        full_name=data['full_name'].strip(),
        specialization=data.get('specialization', ''),
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        status='pending'
    )
    teacher.set_password(data['password'])
    db.session.add(teacher)
    db.session.commit()

    return success_response(
        teacher.to_dict(),
        "Đăng ký thành công! Vui lòng chờ admin phê duyệt tài khoản.",
        201
    )


# ─── THÔNG TIN TÀI KHOẢN ─────────────────────────────────────────────────────

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    role, uid = get_current_user_id()
    if role == 'admin':
        user = Admin.query.get(uid)
    else:
        user = Teacher.query.get(uid)

    if not user:
        return error_response("Tài khoản không tồn tại", 404)
    return success_response(user.to_dict())


# ─── ĐỔI MẬT KHẨU ────────────────────────────────────────────────────────────

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    role, uid = get_current_user_id()
    data = request.get_json()

    errors = validate_required(data, ['old_password', 'new_password'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if role == 'admin':
        user = Admin.query.get(uid)
    else:
        user = Teacher.query.get(uid)

    if not user or not user.check_password(data['old_password']):
        return error_response("Mật khẩu cũ không đúng", 400)

    if len(data['new_password']) < 6:
        return error_response("Mật khẩu mới phải có ít nhất 6 ký tự", 400)

    user.set_password(data['new_password'])
    db.session.commit()
    return success_response(message="Đổi mật khẩu thành công")