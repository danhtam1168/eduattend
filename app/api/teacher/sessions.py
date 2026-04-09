from datetime import date
from flask import Blueprint, request
from app.extensions import db
from app.models.schedule import Schedule
from app.models.teacher_attendance import TeacherAttendance
from app.models.student_attendance import StudentAttendance
from app.models.student_class import StudentClass
from app.utils.response import success_response, error_response
from app.utils.decorators import teacher_required, get_current_teacher
from app.utils.validators import validate_month_format

teacher_sessions_bp = Blueprint('teacher_sessions', __name__)


@teacher_sessions_bp.route('/schedule', methods=['GET'])
@teacher_required
def get_schedule():
    """Lấy lịch dạy của giáo viên"""
    teacher = get_current_teacher()
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    month = request.args.get('month')  # YYYY-MM

    query = Schedule.query.filter_by(teacher_id=teacher.id)

    if month:
        if not validate_month_format(month):
            return error_response("Tháng không đúng định dạng YYYY-MM", 400)
        year, mon = month.split('-')
        query = query.filter(
            db.extract('year',  Schedule.schedule_date) == int(year),
            db.extract('month', Schedule.schedule_date) == int(mon),
        )
    if from_date:
        query = query.filter(Schedule.schedule_date >= date.fromisoformat(from_date))
    if to_date:
        query = query.filter(Schedule.schedule_date <= date.fromisoformat(to_date))

    schedules = query.order_by(Schedule.schedule_date.asc()).all()

    # Gắn thêm thông tin chấm công
    results = []
    for s in schedules:
        d = s.to_dict()
        att = TeacherAttendance.query.filter_by(
            teacher_id=teacher.id, class_id=s.class_id, attendance_date=s.schedule_date
        ).first()
        d['teacher_attendance'] = att.to_dict(include_relations=False) if att else None
        results.append(d)

    return success_response(results)


@teacher_sessions_bp.route('/schedule/today', methods=['GET'])
@teacher_required
def get_today_schedule():
    teacher = get_current_teacher()
    today = date.today()

    schedules = Schedule.query.filter_by(teacher_id=teacher.id, schedule_date=today).all()
    results = []
    for s in schedules:
        d = s.to_dict()
        att = TeacherAttendance.query.filter_by(
            teacher_id=teacher.id, class_id=s.class_id, attendance_date=today
        ).first()
        d['teacher_attendance'] = att.to_dict(include_relations=False) if att else None
        results.append(d)

    return success_response(results)


@teacher_sessions_bp.route('/checkin', methods=['POST'])
@teacher_required
def checkin():
    """Giáo viên tự chấm công (check-in buổi dạy)"""
    teacher = get_current_teacher()
    data = request.get_json() or {}

    class_id = data.get('class_id')
    att_date = data.get('attendance_date', date.today().isoformat())

    if not class_id:
        return error_response("Vui lòng cung cấp class_id", 400)

    existing = TeacherAttendance.query.filter_by(
        teacher_id=teacher.id, class_id=int(class_id), attendance_date=att_date
    ).first()
    if existing:
        return error_response("Bạn đã chấm công buổi này rồi", 409)

    # Kiểm tra lịch tồn tại
    sched = Schedule.query.filter_by(class_id=int(class_id), schedule_date=att_date).first()
    if not sched:
        return error_response("Không tìm thấy lịch dạy cho lớp này trong ngày hôm nay", 404)
    if sched.teacher_id != teacher.id:
        return error_response("Đây không phải lịch dạy của bạn", 403)

    att = TeacherAttendance(
        teacher_id=teacher.id,
        class_id=int(class_id),
        schedule_id=sched.id,
        attendance_date=date.fromisoformat(att_date),
        session_count=float(data.get('session_count', 1)),
        status='present',
        notes=data.get('notes', ''),
    )
    db.session.add(att)
    db.session.commit()

    return success_response(att.to_dict(), "Chấm công thành công", 201)
