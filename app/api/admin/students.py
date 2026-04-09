from flask import Blueprint, request
from app.services.student_service import StudentService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

students_bp = Blueprint('admin_students', __name__)

@students_bp.route('', methods=['GET'])
@admin_required
def get_students():
    try:
        status = request.args.get('status')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        items, total = StudentService.get_students(status, search, page, per_page)
        return paginated_response([s.to_dict() for s in items], total, page, per_page)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@students_bp.route('', methods=['POST'])
@admin_required
def create_student():
    data = request.get_json()
    errors = validate_required(data, ['full_name'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        student = StudentService.create_student(data)
        return success_response(student.to_dict(), "Thêm học sinh thành công", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@students_bp.route('/<int:student_id>', methods=['GET'])
@admin_required
def get_student(student_id):
    try:
        student = StudentService.get_student(student_id)
        return success_response(student.to_dict())
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@students_bp.route('/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    data = request.get_json()
    from app.extensions import db
    try:
        student = StudentService.update_student(student_id, data)
        return success_response(student.to_dict(), "Cập nhật thành công")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@students_bp.route('/<int:student_id>', methods=['DELETE'])
@admin_required
def deactivate_student(student_id):
    from app.extensions import db
    try:
        StudentService.deactivate_student(student_id)
        return success_response(message="Đã khoá hồ sơ học sinh")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
