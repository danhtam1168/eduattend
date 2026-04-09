from flask import Blueprint, request
from app.extensions import db
from app.models.student import Student
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

students_bp = Blueprint('admin_students', __name__)


def _generate_student_code():
    last = Student.query.filter(
        Student.student_code.isnot(None)
    ).order_by(Student.student_code.desc()).first()
    if last and last.student_code:
        try:
            num = int(last.student_code[2:]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"HS{num:03d}"


@students_bp.route('', methods=['GET'])
@admin_required
def get_students():
    status = request.args.get('status')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    query = Student.query.filter_by(is_active=True)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(Student.full_name.ilike(f'%{search}%'))

    total = query.count()
    students = query.order_by(Student.full_name).paginate(page=page, per_page=per_page, error_out=False)
    return paginated_response([s.to_dict() for s in students.items], total, page, per_page)


@students_bp.route('', methods=['POST'])
@admin_required
def create_student():
    data = request.get_json()
    errors = validate_required(data, ['full_name'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    student = Student(
        student_code=_generate_student_code(),
        full_name=data['full_name'].strip(),
        date_of_birth=data.get('date_of_birth'),
        referred_by=data.get('referred_by'),
        address=data.get('address', ''),
        parent_phone=data.get('parent_phone', ''),
        phone=data.get('phone', ''),
        notes=data.get('notes', ''),
        status='active'
    )
    db.session.add(student)
    db.session.commit()
    return success_response(student.to_dict(), "Thêm học sinh thành công", 201)


@students_bp.route('/<int:student_id>', methods=['GET'])
@admin_required
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return error_response("Học sinh không tồn tại", 404)
    return success_response(student.to_dict())


@students_bp.route('/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return error_response("Học sinh không tồn tại", 404)

    data = request.get_json()
    editable = ['full_name', 'date_of_birth', 'referred_by', 'address',
                'parent_phone', 'phone', 'status', 'notes', 'is_active']
    for field in editable:
        if field in data:
            setattr(student, field, data[field])

    db.session.commit()
    return success_response(student.to_dict(), "Cập nhật thành công")


@students_bp.route('/<int:student_id>', methods=['DELETE'])
@admin_required
def deactivate_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return error_response("Học sinh không tồn tại", 404)
    student.is_active = False
    student.status = 'inactive'
    db.session.commit()
    return success_response(message="Đã khoá hồ sơ học sinh")
