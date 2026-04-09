from flask import Blueprint, request
from app.services.teacher_service import TeacherService
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

    from app.extensions import db
    try:
        updated_teacher = TeacherService.update_profile(teacher, data)
        return success_response(updated_teacher.to_dict(include_sensitive=True), "Cập nhật thông tin thành công")
    except ValueError as e:
        if "sử dụng" in str(e).lower():
            return error_response(str(e), 409)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
