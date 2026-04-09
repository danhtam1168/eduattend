from flask import Blueprint, request
from app.services.attendance_service import AttendanceService
from app.utils.response import success_response, error_response
from app.utils.decorators import teacher_required, get_current_teacher

teacher_attendance_bp = Blueprint('teacher_attendance', __name__)

@teacher_attendance_bp.route('/sessions/<int:schedule_id>/students', methods=['GET'])
@teacher_required
def get_session_students(schedule_id):
    """Lấy danh sách học sinh của 1 buổi để điểm danh"""
    try:
        teacher = get_current_teacher()
        data = AttendanceService.get_session_students(schedule_id, teacher.id)
        return success_response(data)
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        if "không phải lịch" in str(e).lower():
            return error_response(str(e), 403)
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_attendance_bp.route('/sessions/<int:schedule_id>/attendance', methods=['POST'])
@teacher_required
def mark_attendance(schedule_id):
    """Giáo viên điểm danh học sinh"""
    data = request.get_json()
    attendances = data.get('attendances', [])
    from app.extensions import db
    try:
        teacher = get_current_teacher()
        total, present = AttendanceService.mark_student_attendance(schedule_id, teacher.id, attendances)
        return success_response({
            "total":   total,
            "present": present,
            "absent":  total - present,
        }, "Điểm danh thành công")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        if "không phải lịch" in str(e).lower():
            return error_response(str(e), 403)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
