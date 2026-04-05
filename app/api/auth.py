from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models.user import User
from app.utils.response import success_response, error_response
from app.utils.validators import validate_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return error_response("Dữ liệu không hợp lệ", 400)

    # Validate required
    errors = validate_required(data, ['employee_id', 'password'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    # Tìm user
    user = User.query.filter_by(employee_id=data['employee_id'].strip()).first()
    if not user or not user.check_password(data['password']):
        return error_response("Mã nhân viên hoặc mật khẩu không đúng", 401)

    if not user.is_active:
        return error_response("Tài khoản đã bị khoá, vui lòng liên hệ admin", 401)

    # Tạo token
    access_token = create_access_token(identity=user.id)

    return success_response({
        "access_token": access_token,
        "user": user.to_dict()
    }, "Đăng nhập thành công")


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error_response("Tài khoản không tồn tại", 404)
    return success_response(user.to_dict())


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()

    errors = validate_required(data, ['old_password', 'new_password'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if not user.check_password(data['old_password']):
        return error_response("Mật khẩu cũ không đúng", 400)

    if len(data['new_password']) < 6:
        return error_response("Mật khẩu mới phải có ít nhất 6 ký tự", 400)

    user.set_password(data['new_password'])
    from app.extensions import db
    db.session.commit()

    return success_response(message="Đổi mật khẩu thành công")