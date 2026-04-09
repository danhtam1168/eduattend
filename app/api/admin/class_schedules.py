from flask import Blueprint, request
from app.services.class_schedule_service import ClassScheduleService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

class_schedules_bp = Blueprint('admin_class_schedules', __name__)

@class_schedules_bp.route('', methods=['GET'])
@admin_required
def get_templates():
    try:
        class_id = request.args.get('class_id')
        if class_id:
            class_id = int(class_id)
            
        templates = ClassScheduleService.get_templates(class_id)
        return success_response([t.to_dict() for t in templates])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@class_schedules_bp.route('', methods=['POST'])
@admin_required
def create_template():
    data = request.get_json()
    errors = validate_required(data, ['class_id', 'day_of_week', 'start_time', 'end_time'])
    if errors:
        return error_response("Thiếu dữ liệu", 400, errors)

    from app.extensions import db
    try:
        tpl = ClassScheduleService.create_template(data)
        return success_response(tpl.to_dict(), "Đã lên mẫu lịch. Các buổi học đã tự động sinh ra hợp lệ.", 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@class_schedules_bp.route('/<int:template_id>', methods=['DELETE'])
@admin_required
def delete_template(template_id):
    from app.extensions import db
    try:
        ClassScheduleService.delete_template(template_id)
        return success_response(message="Đã xoá mẫu lịch")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
