from datetime import date
from flask import Blueprint, request
from app.extensions import db
from app.models.student_attendance import StudentAttendance
from app.models.teacher_attendance import TeacherAttendance
from app.models.student_class import StudentClass
from app.utils.response import success_response, error_response
from app.utils.decorators import teacher_required, get_current_teacher

teacher_attendance_bp = Blueprint('teacher_attendance', __name__)

VALID_STATUSES = ('present', 'absent_excused', 'absent_unexcused', 'teacher_cancelled')


@teacher_attendance_bp.route('/sessions/<int:schedule_id>/students', methods=['GET'])
@teacher_required
def get_session_students(schedule_id):
    """Lấy danh sách học sinh của 1 buổi để điểm danh"""
    from app.models.schedule import Schedule
    teacher = get_current_teacher()

    sched = Schedule.query.get(schedule_id)
    if not sched:
        return error_response("Lịch học không tồn tại", 404)
    if sched.teacher_id != teacher.id:
        return error_response("Đây không phải lịch dạy của bạn", 403)

    # Kiểm tra giáo viên đã chấm công chưa
    teacher_att = TeacherAttendance.query.filter_by(
        teacher_id=teacher.id, class_id=sched.class_id, attendance_date=sched.schedule_date
    ).first()
    if not teacher_att:
        return error_response("Vui lòng chấm công trước khi điểm danh học sinh", 400)

    # Lấy danh sách học sinh của lớp
    enrollments = StudentClass.query.filter_by(class_id=sched.class_id, status='active').all()

    # Map điểm danh hiện tại
    att_map = {}
    for att in StudentAttendance.query.filter_by(
        class_id=sched.class_id, attendance_date=sched.schedule_date
    ).all():
        att_map[att.student_id] = att

    result = []
    for enr in enrollments:
        s = enr.student
        att = att_map.get(s.id)
        result.append({
            **s.to_dict(),
            "attendance_status": att.status if att else None,
            "attendance_note":   att.notes if att else None,
            "attendance_id":     att.id if att else None,
        })

    return success_response({
        "schedule": sched.to_dict(),
        "teacher_attendance": teacher_att.to_dict(include_relations=False),
        "students": result,
    })


@teacher_attendance_bp.route('/sessions/<int:schedule_id>/attendance', methods=['POST'])
@teacher_required
def mark_attendance(schedule_id):
    """Giáo viên điểm danh học sinh"""
    from app.models.schedule import Schedule
    teacher = get_current_teacher()

    sched = Schedule.query.get(schedule_id)
    if not sched:
        return error_response("Lịch học không tồn tại", 404)
    if sched.teacher_id != teacher.id:
        return error_response("Đây không phải lịch dạy của bạn", 403)

    teacher_att = TeacherAttendance.query.filter_by(
        teacher_id=teacher.id, class_id=sched.class_id, attendance_date=sched.schedule_date
    ).first()
    if not teacher_att:
        return error_response("Vui lòng chấm công trước khi điểm danh học sinh", 400)

    data = request.get_json()
    attendances = data.get('attendances', [])
    if not attendances:
        return error_response("Danh sách điểm danh không được để trống", 400)

    present_count = 0
    for item in attendances:
        student_id = item.get('student_id')
        status = item.get('status', 'present')
        note = item.get('note', '')

        if not student_id:
            continue
        if status not in VALID_STATUSES:
            return error_response(f"Trạng thái không hợp lệ: {status}. Phải là: {', '.join(VALID_STATUSES)}", 400)

        existing = StudentAttendance.query.filter_by(
            student_id=int(student_id), class_id=sched.class_id, attendance_date=sched.schedule_date
        ).first()

        if existing:
            existing.status = status
            existing.notes = note
        else:
            existing = StudentAttendance(
                student_id=int(student_id),
                class_id=sched.class_id,
                teacher_attendance_id=teacher_att.id,
                attendance_date=sched.schedule_date,
                status=status,
                notes=note,
                teacher_id=teacher.id,
            )
            db.session.add(existing)

        if status == 'present':
            present_count += 1

    db.session.commit()
    return success_response({
        "total":   len(attendances),
        "present": present_count,
        "absent":  len(attendances) - present_count,
    }, "Điểm danh thành công")
