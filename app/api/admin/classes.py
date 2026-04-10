from flask import Blueprint, request
from app.services.class_service import ClassService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

classes_bp = Blueprint('admin_classes', __name__)

@classes_bp.route('', methods=['GET'])
@admin_required
def get_classes():
    try:
        status = request.args.get('status')
        teacher_id = request.args.get('teacher_id')
        subject_id = request.args.get('subject_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        items, total = ClassService.get_classes(status, teacher_id, subject_id, page, per_page)
        return paginated_response([c.to_dict(include_students=True) for c in items], total, page, per_page)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@classes_bp.route('', methods=['POST'])
@admin_required
def create_class():
    data = request.get_json()
    errors = validate_required(data, ['class_name', 'subject_id', 'teacher_id', 'start_date'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        cls = ClassService.create_class(data)
        return success_response(cls.to_dict(), "Tạo lớp học thành công", 201)
    except ValueError as e:
        if "tồn tại" in str(e).lower() and "mã lớp" in str(e).lower():
            return error_response(str(e), 409)
        return error_response(str(e), 404 if "không tồn tại" in str(e).lower() else 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@classes_bp.route('/<int:class_id>', methods=['GET'])
@admin_required
def get_class(class_id):
    try:
        cls = ClassService.get_class(class_id)
        return success_response(cls.to_dict())
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@classes_bp.route('/<int:class_id>', methods=['PUT'])
@admin_required
def update_class(class_id):
    data = request.get_json()
    from app.extensions import db
    try:
        cls = ClassService.update_class(class_id, data)
        return success_response(cls.to_dict(), "Cập nhật thành công")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

# ─── QUẢN LÝ HỌC SINH TRONG LỚP ─────────────────────────────────────────────

@classes_bp.route('/<int:class_id>/students', methods=['GET'])
@admin_required
def get_class_students(class_id):
    try:
        enrollments = ClassService.get_class_students(class_id)
        return success_response([e.to_dict(include_student=True) for e in enrollments])
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@classes_bp.route('/<int:class_id>/students', methods=['POST'])
@admin_required
def enroll_student(class_id):
    """Đăng ký học sinh vào lớp"""
    data = request.get_json()
    errors = validate_required(data, ['student_id'])
    if errors:
        return error_response("Thiếu student_id", 400, errors)

    from app.extensions import db
    try:
        enrollment = ClassService.enroll_student(class_id, data)
        return success_response(enrollment.to_dict(), "Đăng ký học thành công", 201)
    except ValueError as e:
        if "đã đăng ký" in str(e).lower():
            return error_response(str(e), 409)
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@classes_bp.route('/<int:class_id>/students/<int:student_id>', methods=['DELETE'])
@admin_required
def remove_student(class_id, student_id):
    from app.extensions import db
    try:
        ClassService.remove_student(class_id, student_id)
        return success_response(message="Đã rút học sinh khỏi lớp")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@classes_bp.route('/<int:class_id>', methods=['DELETE'])
@admin_required
def delete_class(class_id):
    from app.extensions import db
    try:
        ClassService.delete_class(class_id)
        return success_response(message="Đã xoá lớp học")
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
