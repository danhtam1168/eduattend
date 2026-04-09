from flask import Blueprint, request
from app.services.teacher_service import TeacherService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import admin_required, get_current_admin
from app.utils.validators import validate_required

teachers_bp = Blueprint('admin_teachers', __name__)

@teachers_bp.route('', methods=['GET'])
@admin_required
def get_teachers():
    try:
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        items, total = TeacherService.get_teachers(status, page, per_page)
        return paginated_response(
            items=[t.to_dict(include_sensitive=True) for t in items],
            total=total, page=page, per_page=per_page
        )
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teachers_bp.route('', methods=['POST'])
@admin_required
def create_teacher():
    data = request.get_json()
    errors = validate_required(data, ['username', 'password', 'full_name'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        admin = get_current_admin()
        teacher = TeacherService.create_teacher(data, admin.id)
        return success_response(teacher.to_dict(include_sensitive=True), "Tạo giáo viên thành công", 201)
    except ValueError as e:
        if "sử dụng" in str(e).lower():
            return error_response(str(e), 409)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teachers_bp.route('/<int:teacher_id>/approve', methods=['PUT'])
@admin_required
def approve_teacher(teacher_id):
    data = request.get_json() or {}
    from app.extensions import db
    try:
        admin = get_current_admin()
        teacher = TeacherService.approve_teacher(teacher_id, admin.id, data)
        return success_response(teacher.to_dict(include_sensitive=True), f"Đã phê duyệt giáo viên. Mã GV: {teacher.teacher_code}")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teachers_bp.route('/<int:teacher_id>/reject', methods=['PUT'])
@admin_required
def reject_teacher(teacher_id):
    data = request.get_json() or {}
    from app.extensions import db
    try:
        TeacherService.reject_teacher(teacher_id, data)
        return success_response(message="Đã từ chối tài khoản giáo viên")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(teacher_id):
    data = request.get_json()
    from app.extensions import db
    try:
        teacher = TeacherService.update_teacher(teacher_id, data)
        return success_response(teacher.to_dict(include_sensitive=True), "Cập nhật thành công")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
@admin_required
def deactivate_teacher(teacher_id):
    from app.extensions import db
    try:
        TeacherService.deactivate_teacher(teacher_id)
        return success_response(message="Đã khoá tài khoản giáo viên")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
@admin_required
def get_teacher(teacher_id):
    try:
        teacher = TeacherService.get_teacher(teacher_id)
        return success_response(teacher.to_dict(include_sensitive=True))
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
