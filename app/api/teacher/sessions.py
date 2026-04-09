from flask import Blueprint, request
from app.services.session_service import SessionService
from app.utils.response import success_response, error_response
from app.utils.decorators import teacher_required, get_current_teacher

teacher_sessions_bp = Blueprint('teacher_sessions', __name__)

@teacher_sessions_bp.route('/schedule', methods=['GET'])
@teacher_required
def get_schedule():
    """Lấy lịch dạy của giáo viên"""
    try:
        teacher = get_current_teacher()
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        month = request.args.get('month')  # YYYY-MM
        
        results = SessionService.get_teacher_schedule(teacher.id, month, from_date, to_date)
        return success_response(results)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_sessions_bp.route('/schedule/today', methods=['GET'])
@teacher_required
def get_today_schedule():
    try:
        teacher = get_current_teacher()
        results = SessionService.get_today_schedule(teacher.id)
        return success_response(results)
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@teacher_sessions_bp.route('/checkin', methods=['POST'])
@teacher_required
def checkin():
    """Giáo viên tự chấm công (check-in buổi dạy)"""
    data = request.get_json() or {}
    from app.extensions import db
    try:
        teacher = get_current_teacher()
        att = SessionService.checkin(teacher.id, data)
        return success_response(att.to_dict(), "Chấm công thành công", 201)
    except ValueError as e:
        if "chấm công buổi này rồi" in str(e).lower():
            return error_response(str(e), 409)
        if "không tìm thấy lịch" in str(e).lower():
            return error_response(str(e), 404)
        if "không phải lịch" in str(e).lower():
            return error_response(str(e), 403)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
