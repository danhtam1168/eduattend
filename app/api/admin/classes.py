from datetime import date
from flask import Blueprint, request
from app.extensions import db
from app.models.class_ import Class
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.student_class import StudentClass
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

classes_bp = Blueprint('admin_classes', __name__)


@classes_bp.route('', methods=['GET'])
@admin_required
def get_classes():
    status = request.args.get('status')
    teacher_id = request.args.get('teacher_id')
    subject_id = request.args.get('subject_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = Class.query
    if status:
        query = query.filter_by(status=status)
    if teacher_id:
        query = query.filter_by(teacher_id=int(teacher_id))
    if subject_id:
        query = query.filter_by(subject_id=int(subject_id))

    total = query.count()
    classes = query.order_by(Class.start_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return paginated_response([c.to_dict() for c in classes.items], total, page, per_page)


@classes_bp.route('', methods=['POST'])
@admin_required
def create_class():
    data = request.get_json()
    errors = validate_required(data, ['class_name', 'subject_id', 'teacher_id', 'start_date'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if not Subject.query.get(data['subject_id']):
        return error_response("Môn học không tồn tại", 404)

    teacher = Teacher.query.get(data['teacher_id'])
    if not teacher or teacher.status != 'active':
        return error_response("Giáo viên không tồn tại hoặc chưa được kích hoạt", 404)

    if data.get('class_code') and Class.query.filter_by(class_code=data['class_code']).first():
        return error_response("Mã lớp đã tồn tại", 409)

    cls = Class(
        class_name=data['class_name'].strip(),
        class_code=data.get('class_code', '').strip() or None,
        subject_id=int(data['subject_id']),
        teacher_id=int(data['teacher_id']),
        room_id=data.get('room_id'),
        max_students=data.get('max_students', 15),
        start_date=date.fromisoformat(data['start_date']),
        end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
        schedule_days=data.get('schedule_days', ''),
        schedule_time=data.get('schedule_time'),
        duration_minutes=data.get('duration_minutes', 90),
        notes=data.get('notes', ''),
    )
    db.session.add(cls)
    db.session.commit()
    return success_response(cls.to_dict(), "Tạo lớp học thành công", 201)


@classes_bp.route('/<int:class_id>', methods=['GET'])
@admin_required
def get_class(class_id):
    cls = Class.query.get(class_id)
    if not cls:
        return error_response("Lớp học không tồn tại", 404)
    return success_response(cls.to_dict())


@classes_bp.route('/<int:class_id>', methods=['PUT'])
@admin_required
def update_class(class_id):
    cls = Class.query.get(class_id)
    if not cls:
        return error_response("Lớp học không tồn tại", 404)

    data = request.get_json()
    editable = ['class_name', 'class_code', 'teacher_id', 'room_id',
                'max_students', 'end_date', 'schedule_days', 'schedule_time',
                'duration_minutes', 'status', 'notes']
    for field in editable:
        if field in data:
            setattr(cls, field, data[field])

    db.session.commit()
    return success_response(cls.to_dict(), "Cập nhật thành công")


# ─── QUẢN LÝ HỌC SINH TRONG LỚP ─────────────────────────────────────────────

@classes_bp.route('/<int:class_id>/students', methods=['GET'])
@admin_required
def get_class_students(class_id):
    cls = Class.query.get(class_id)
    if not cls:
        return error_response("Lớp học không tồn tại", 404)

    enrollments = StudentClass.query.filter_by(class_id=class_id, status='active').all()
    return success_response([e.to_dict(include_student=True) for e in enrollments])


@classes_bp.route('/<int:class_id>/students', methods=['POST'])
@admin_required
def enroll_student(class_id):
    """Đăng ký học sinh vào lớp"""
    cls = Class.query.get(class_id)
    if not cls:
        return error_response("Lớp học không tồn tại", 404)
    if cls.status != 'active':
        return error_response("Lớp học không còn hoạt động", 400)
    if cls.current_students >= cls.max_students:
        return error_response("Lớp học đã đầy", 400)

    data = request.get_json()
    errors = validate_required(data, ['student_id'])
    if errors:
        return error_response("Thiếu student_id", 400, errors)

    student = Student.query.get(int(data['student_id']))
    if not student or not student.is_active:
        return error_response("Học sinh không tồn tại", 404)

    if StudentClass.query.filter_by(class_id=class_id, student_id=student.id, status='active').first():
        return error_response("Học sinh đã đăng ký lớp này", 409)

    # Học phí = lấy từ lớp → subject.fee_per_session, có thể override
    fee = float(data.get('fee_amount', cls.subject.fee_per_session))
    discount_percent = float(data.get('discount_percent', 0))
    discount_amount = fee * discount_percent / 100
    final_fee = fee - discount_amount

    enrollment = StudentClass(
        student_id=student.id,
        class_id=class_id,
        fee_amount=fee,
        discount_percent=discount_percent,
        discount_amount=discount_amount,
        final_fee=final_fee,
        notes=data.get('notes', '')
    )
    cls.current_students = (cls.current_students or 0) + 1
    db.session.add(enrollment)
    db.session.commit()

    return success_response(enrollment.to_dict(), "Đăng ký học thành công", 201)


@classes_bp.route('/<int:class_id>/students/<int:student_id>', methods=['DELETE'])
@admin_required
def remove_student(class_id, student_id):
    enrollment = StudentClass.query.filter_by(class_id=class_id, student_id=student_id, status='active').first()
    if not enrollment:
        return error_response("Học sinh chưa đăng ký lớp này", 404)

    enrollment.status = 'dropped'
    cls = Class.query.get(class_id)
    if cls and cls.current_students > 0:
        cls.current_students -= 1
    db.session.commit()
    return success_response(message="Đã rút học sinh khỏi lớp")
