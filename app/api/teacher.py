from datetime import datetime, date
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.teaching_session import TeachingSession
from app.models.attendance import StudentAttendance
from app.models.student import Student
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import teacher_required
from app.utils.validators import validate_month_format

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/sessions', methods=['GET'])
@teacher_required
def get_my_sessions():
    """Lấy danh sách buổi dạy của giáo viên theo tháng"""
    teacher_id = get_jwt_identity()
    month = request.args.get('month')  # format: YYYY-MM
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = TeachingSession.query.filter_by(teacher_id=teacher_id)

    if month:
        if not validate_month_format(month):
            return error_response("Tháng không đúng định dạng YYYY-MM", 400)
        year, mon = month.split('-')
        query = query.filter(
            db.extract('year', TeachingSession.date) == int(year),
            db.extract('month', TeachingSession.date) == int(mon)
        )

    query = query.order_by(TeachingSession.date.desc(), TeachingSession.shift)
    total = query.count()
    sessions = query.paginate(page=page, per_page=per_page, error_out=False)

    return paginated_response(
        items=[s.to_dict() for s in sessions.items],
        total=total,
        page=page,
        per_page=per_page
    )


@teacher_bp.route('/sessions/today', methods=['GET'])
@teacher_required
def get_today_sessions():
    """Lấy buổi dạy hôm nay của giáo viên"""
    teacher_id = get_jwt_identity()
    today = date.today()

    sessions = TeachingSession.query.filter_by(
        teacher_id=teacher_id,
        date=today
    ).order_by(TeachingSession.shift).all()

    return success_response([s.to_dict() for s in sessions])


@teacher_bp.route('/sessions/<int:session_id>', methods=['GET'])
@teacher_required
def get_session_detail(session_id):
    """Chi tiết một buổi dạy"""
    teacher_id = get_jwt_identity()
    session = TeachingSession.query.get(session_id)

    if not session:
        return error_response("Buổi dạy không tồn tại", 404)
    if session.teacher_id != teacher_id:
        return error_response("Bạn không có quyền xem buổi dạy này", 403)

    return success_response(session.to_dict(include_attendances=True))


@teacher_bp.route('/sessions/<int:session_id>/confirm', methods=['POST'])
@teacher_required
def confirm_session(session_id):
    """Giáo viên xác nhận có dạy buổi này"""
    teacher_id = get_jwt_identity()
    session = TeachingSession.query.get(session_id)

    if not session:
        return error_response("Buổi dạy không tồn tại", 404)
    if session.teacher_id != teacher_id:
        return error_response("Bạn không có quyền xác nhận buổi dạy này", 403)
    if session.status == 'confirmed':
        return error_response("Buổi dạy đã được xác nhận trước đó", 409)
    if session.status == 'cancelled':
        return error_response("Buổi dạy đã bị huỷ, không thể xác nhận", 400)

    session.status = 'confirmed'
    session.confirmed_at = datetime.utcnow()
    db.session.commit()

    return success_response(session.to_dict(), "Xác nhận buổi dạy thành công")


@teacher_bp.route('/sessions/<int:session_id>/attendance', methods=['POST'])
@teacher_required
def mark_attendance(session_id):
    """Giáo viên điểm danh học sinh cho buổi dạy"""
    teacher_id = get_jwt_identity()
    session = TeachingSession.query.get(session_id)

    if not session:
        return error_response("Buổi dạy không tồn tại", 404)
    if session.teacher_id != teacher_id:
        return error_response("Bạn không có quyền điểm danh buổi dạy này", 403)
    if session.status != 'confirmed':
        return error_response("Cần xác nhận buổi dạy trước khi điểm danh", 400)

    data = request.get_json()
    attendances = data.get('attendances', [])
    if not attendances:
        return error_response("Danh sách điểm danh không được để trống", 400)

    present_count = 0
    for item in attendances:
        student_id = item.get('student_id')
        is_present = item.get('is_present', False)
        note = item.get('note', '')

        if not student_id:
            continue

        # Upsert — nếu đã có thì update, chưa có thì tạo mới
        attendance = StudentAttendance.query.filter_by(
            session_id=session_id,
            student_id=student_id
        ).first()

        if attendance:
            attendance.is_present = is_present
            attendance.note = note
        else:
            attendance = StudentAttendance(
                session_id=session_id,
                student_id=student_id,
                is_present=is_present,
                note=note
            )
            db.session.add(attendance)

        if is_present:
            present_count += 1

    db.session.commit()

    return success_response({
        "total":   len(attendances),
        "present": present_count,
        "absent":  len(attendances) - present_count
    }, "Điểm danh thành công")


@teacher_bp.route('/sessions/<int:session_id>/students', methods=['GET'])
@teacher_required
def get_session_students(session_id):
    """Lấy danh sách học sinh của buổi dạy để điểm danh"""
    teacher_id = get_jwt_identity()
    session = TeachingSession.query.get(session_id)

    if not session:
        return error_response("Buổi dạy không tồn tại", 404)
    if session.teacher_id != teacher_id:
        return error_response("Bạn không có quyền xem buổi dạy này", 403)

    # Lấy học sinh cùng lớp với buổi dạy
    class_type = session.salary_rate.class_type
    students = Student.query.filter_by(class_name=class_type, is_active=True).all()

    # Lấy trạng thái điểm danh nếu đã có
    attended_map = {}
    for att in session.attendances:
        attended_map[att.student_id] = att

    result = []
    for student in students:
        att = attended_map.get(student.id)
        result.append({
            **student.to_dict(),
            "is_present": att.is_present if att else None,
            "att_note":   att.note if att else None,
        })

    return success_response(result)


@teacher_bp.route('/profile', methods=['PUT'])
@teacher_required
def update_profile():
    """Giáo viên cập nhật thông tin cá nhân"""
    from app.models.user import User
    teacher_id = get_jwt_identity()
    user = User.query.get(teacher_id)
    data = request.get_json()

    # Chỉ cho phép cập nhật các field an toàn
    if 'phone' in data:
        user.phone = data['phone']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return success_response(user.to_dict(), "Cập nhật thông tin thành công")