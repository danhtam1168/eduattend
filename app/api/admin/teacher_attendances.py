from datetime import date
from flask import Blueprint, request
from app.extensions import db
from app.models.teacher_attendance import TeacherAttendance
from app.models.student_attendance import StudentAttendance
from app.models.schedule import Schedule
from app.models.class_ import Class
from app.models.student_class import StudentClass
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required, get_current_admin
from app.utils.validators import validate_required

teacher_attendances_bp = Blueprint('admin_teacher_attendances', __name__)


@teacher_attendances_bp.route('', methods=['GET'])
@admin_required
def get_teacher_attendances():
    teacher_id = request.args.get('teacher_id')
    class_id = request.args.get('class_id')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    query = TeacherAttendance.query
    if teacher_id:
        query = query.filter_by(teacher_id=int(teacher_id))
    if class_id:
        query = query.filter_by(class_id=int(class_id))
    if from_date:
        query = query.filter(TeacherAttendance.attendance_date >= date.fromisoformat(from_date))
    if to_date:
        query = query.filter(TeacherAttendance.attendance_date <= date.fromisoformat(to_date))

    records = query.order_by(TeacherAttendance.attendance_date.desc()).all()
    return success_response([r.to_dict() for r in records])


@teacher_attendances_bp.route('', methods=['POST'])
@admin_required
def create_teacher_attendance():
    """Admin ghi chấm công giáo viên"""
    data = request.get_json()
    errors = validate_required(data, ['teacher_id', 'class_id', 'attendance_date'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    existing = TeacherAttendance.query.filter_by(
        teacher_id=int(data['teacher_id']),
        class_id=int(data['class_id']),
        attendance_date=data['attendance_date']
    ).first()
    if existing:
        return error_response("Đã có bản ghi chấm công cho giáo viên này trong ngày", 409)

    sched = Schedule.query.filter_by(
        class_id=int(data['class_id']),
        schedule_date=data['attendance_date']
    ).first()

    admin = get_current_admin()
    record = TeacherAttendance(
        teacher_id=int(data['teacher_id']),
        class_id=int(data['class_id']),
        schedule_id=sched.id if sched else None,
        attendance_date=date.fromisoformat(data['attendance_date']),
        session_count=float(data.get('session_count', 1)),
        status=data.get('status', 'present'),
        notes=data.get('notes', ''),
        recorded_by=admin.id if admin else None,
    )
    db.session.add(record)

    # Nếu GV bị absent → đánh dấu toàn bộ HS là teacher_cancelled
    if record.status == 'absent':
        enrollments = StudentClass.query.filter_by(class_id=record.class_id, status='active').all()
        for enr in enrollments:
            if not StudentAttendance.query.filter_by(
                student_id=enr.student_id, class_id=record.class_id,
                attendance_date=record.attendance_date
            ).first():
                sa = StudentAttendance(
                    student_id=enr.student_id,
                    class_id=record.class_id,
                    teacher_attendance_id=record.id,
                    attendance_date=record.attendance_date,
                    status='teacher_cancelled',
                    teacher_id=record.teacher_id,
                )
                db.session.add(sa)

    db.session.commit()
    return success_response(record.to_dict(), "Ghi chấm công thành công", 201)


@teacher_attendances_bp.route('/<int:record_id>', methods=['PUT'])
@admin_required
def update_teacher_attendance(record_id):
    record = TeacherAttendance.query.get(record_id)
    if not record:
        return error_response("Bản ghi không tồn tại", 404)

    data = request.get_json()
    editable = ['status', 'session_count', 'notes']
    for field in editable:
        if field in data:
            setattr(record, field, data[field])

    db.session.commit()
    return success_response(record.to_dict(), "Cập nhật thành công")
