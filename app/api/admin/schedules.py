from datetime import date, datetime, time
from flask import Blueprint, request
from app.extensions import db
from app.models.schedule import Schedule
from app.models.class_ import Class
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required, validate_date_format

schedules_bp = Blueprint('admin_schedules', __name__)


@schedules_bp.route('', methods=['GET'])
@admin_required
def get_schedules():
    class_id = request.args.get('class_id')
    teacher_id = request.args.get('teacher_id')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    status = request.args.get('status')

    query = Schedule.query
    if class_id:
        query = query.filter_by(class_id=int(class_id))
    if teacher_id:
        query = query.filter_by(teacher_id=int(teacher_id))
    if from_date:
        query = query.filter(Schedule.schedule_date >= date.fromisoformat(from_date))
    if to_date:
        query = query.filter(Schedule.schedule_date <= date.fromisoformat(to_date))
    if status:
        query = query.filter_by(status=status)

    schedules = query.order_by(Schedule.schedule_date.desc()).all()
    return success_response([s.to_dict() for s in schedules])


@schedules_bp.route('', methods=['POST'])
@admin_required
def create_schedule():
    data = request.get_json()
    errors = validate_required(data, ['class_id', 'schedule_date', 'start_time', 'end_time'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    cls = Class.query.get(int(data['class_id']))
    if not cls or cls.status != 'active':
        return error_response("Lớp học không tồn tại hoặc không còn hoạt động", 404)

    if Schedule.query.filter_by(class_id=cls.id, schedule_date=data['schedule_date']).first():
        return error_response("Lớp học đã có lịch trong ngày này", 409)

    sched = Schedule(
        class_id=cls.id,
        teacher_id=data.get('teacher_id', cls.teacher_id),
        schedule_date=date.fromisoformat(data['schedule_date']),
        start_time=time.fromisoformat(data['start_time']),
        end_time=time.fromisoformat(data['end_time']),
        room_id=data.get('room_id', cls.room_id),
        notes=data.get('notes', ''),
    )
    db.session.add(sched)
    db.session.commit()
    return success_response(sched.to_dict(), "Tạo lịch học thành công", 201)


@schedules_bp.route('/<int:schedule_id>', methods=['PUT'])
@admin_required
def update_schedule(schedule_id):
    sched = Schedule.query.get(schedule_id)
    if not sched:
        return error_response("Lịch học không tồn tại", 404)

    data = request.get_json()
    editable = ['start_time', 'end_time', 'room_id', 'status', 'notes', 'teacher_id']
    for field in editable:
        if field in data:
            setattr(sched, field, data[field])

    db.session.commit()
    return success_response(sched.to_dict(), "Cập nhật lịch học thành công")


@schedules_bp.route('/<int:schedule_id>', methods=['DELETE'])
@admin_required
def cancel_schedule(schedule_id):
    sched = Schedule.query.get(schedule_id)
    if not sched:
        return error_response("Lịch học không tồn tại", 404)
    sched.status = 'cancelled'
    db.session.commit()
    return success_response(message="Đã huỷ lịch học")
