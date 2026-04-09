from flask import Blueprint, request
from app.services.attendance_service import AttendanceService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required, get_current_admin
from app.utils.validators import validate_required

teacher_attendances_bp = Blueprint('admin_teacher_attendances', __name__)

@teacher_attendances_bp.route('', methods=['GET'])
@admin_required
def get_teacher_attendances():
    try:
        teacher_id = request.args.get('teacher_id')
        class_id = request.args.get('class_id')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        records = AttendanceService.get_teacher_attendances(teacher_id, class_id, from_date, to_date)
        return success_response([r.to_dict() for r in records])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_attendances_bp.route('', methods=['POST'])
@admin_required
def create_teacher_attendance():
    """Admin ghi chấm công giáo viên"""
    data = request.get_json()
    errors = validate_required(data, ['teacher_id', 'class_id', 'attendance_date'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        admin = get_current_admin()
        record = AttendanceService.create_teacher_attendance(data, admin.id if admin else None)
        return success_response(record.to_dict(), "Ghi chấm công thành công", 201)
    except ValueError as e:
        if "đã có bản ghi" in str(e).lower():
            return error_response(str(e), 409)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_attendances_bp.route('/<int:record_id>', methods=['PUT'])
@admin_required
def update_teacher_attendance(record_id):
    data = request.get_json()
    from app.extensions import db
    try:
        record = AttendanceService.update_teacher_attendance(record_id, data)
        return success_response(record.to_dict(), "Cập nhật thành công")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
