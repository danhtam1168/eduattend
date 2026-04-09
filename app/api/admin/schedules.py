from flask import Blueprint, request
from app.services.schedule_service import ScheduleService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

schedules_bp = Blueprint('admin_schedules', __name__)

@schedules_bp.route('', methods=['GET'])
@admin_required
def get_schedules():
    try:
        class_id = request.args.get('class_id')
        teacher_id = request.args.get('teacher_id')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        status = request.args.get('status')
        
        schedules = ScheduleService.get_schedules(class_id, teacher_id, from_date, to_date, status)
        return success_response([s.to_dict() for s in schedules])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@schedules_bp.route('', methods=['POST'])
@admin_required
def create_schedule():
    data = request.get_json()
    errors = validate_required(data, ['class_id', 'schedule_date', 'start_time', 'end_time'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        sched = ScheduleService.create_schedule(data)
        return success_response(sched.to_dict(), "Tạo lịch học thành công", 201)
    except ValueError as e:
        if "đã có lịch" in str(e).lower():
            return error_response(str(e), 409)
        return error_response(str(e), 404 if "không tồn tại" in str(e).lower() else 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@schedules_bp.route('/<int:schedule_id>', methods=['PUT'])
@admin_required
def update_schedule(schedule_id):
    data = request.get_json()
    from app.extensions import db
    try:
        sched = ScheduleService.update_schedule(schedule_id, data)
        return success_response(sched.to_dict(), "Cập nhật lịch học thành công")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@schedules_bp.route('/<int:schedule_id>', methods=['DELETE'])
@admin_required
def cancel_schedule(schedule_id):
    from app.extensions import db
    try:
        ScheduleService.cancel_schedule(schedule_id)
        return success_response(message="Đã huỷ lịch học")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
