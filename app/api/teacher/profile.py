from flask import Blueprint, request
from app.extensions import db
from app.models.teacher import Teacher
from app.models.admin import Admin
from app.utils.response import success_response, error_response
from app.utils.decorators import teacher_required, get_current_teacher

teacher_profile_bp = Blueprint('teacher_profile', __name__)


@teacher_profile_bp.route('/profile', methods=['GET'])
@teacher_required
def get_profile():
    teacher = get_current_teacher()
    if not teacher:
        return error_response("Tài khoản không tồn tại", 404)
    return success_response(teacher.to_dict(include_sensitive=True))


@teacher_profile_bp.route('/profile', methods=['PUT'])
@teacher_required
def update_profile():
    teacher = get_current_teacher()
    data = request.get_json()

    # Giáo viên chỉ được sửa các trường an toàn
    # username có thể đổi, nhưng phải kiểm tra trùng
    if 'username' in data:
        new_username = data['username'].strip()
        if new_username != teacher.username:
            from app.models.admin import Admin
            if Teacher.query.filter_by(username=new_username).first() or \
               Admin.query.filter_by(username=new_username).first():
                return error_response("Username đã được sử dụng", 409)
            teacher.username = new_username

    safe_fields = ['phone', 'address', 'bank_account', 'specialization']
    for field in safe_fields:
        if field in data:
            setattr(teacher, field, data[field])

    db.session.commit()
    return success_response(teacher.to_dict(include_sensitive=True), "Cập nhật thông tin thành công")
