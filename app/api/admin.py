from datetime import datetime
from flask import Blueprint, request
from sqlalchemy import func

from app.extensions import db
from app.models.user import User
from app.models.teaching_session import TeachingSession
from app.models.salary_rate import SalaryRate
from app.models.student import Student
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required, validate_date_format, validate_month_format, validate_shift

admin_bp = Blueprint('admin', __name__)


# ─── QUẢN LÝ GIÁO VIÊN ───────────────────────────────────────────────────────

@admin_bp.route('/teachers', methods=['GET'])
@admin_required
def get_teachers():
    teachers = User.query.filter_by(role='teacher').order_by(User.created_at.desc()).all()
    return success_response([t.to_dict() for t in teachers])


@admin_bp.route('/teachers', methods=['POST'])
@admin_required
def create_teacher():
    data = request.get_json()
    errors = validate_required(data, ['employee_id', 'full_name', 'password'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if User.query.filter_by(employee_id=data['employee_id'].strip()).first():
        return error_response("Mã nhân viên đã tồn tại", 409)

    user = User(
        employee_id=data['employee_id'].strip(),
        full_name=data['full_name'].strip(),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        role='teacher'
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return success_response(user.to_dict(), "Tạo giáo viên thành công", 201)


@admin_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(teacher_id):
    user = User.query.get(teacher_id)
    if not user:
        return error_response("Giáo viên không tồn tại", 404)

    data = request.get_json()
    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'phone' in data:
        user.phone = data['phone']
    if 'email' in data:
        user.email = data['email']
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return success_response(user.to_dict(), "Cập nhật thành công")


@admin_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
@admin_required
def deactivate_teacher(teacher_id):
    """Soft delete — khoá tài khoản thay vì xoá"""
    user = User.query.get(teacher_id)
    if not user:
        return error_response("Giáo viên không tồn tại", 404)

    user.is_active = False
    db.session.commit()
    return success_response(message="Đã khoá tài khoản giáo viên")


# ─── QUẢN LÝ BUỔI DẠY ────────────────────────────────────────────────────────

@admin_bp.route('/sessions', methods=['GET'])
@admin_required
def get_sessions():
    month = request.args.get('month')
    teacher_id = request.args.get('teacher_id')
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = TeachingSession.query

    if month:
        if not validate_month_format(month):
            return error_response("Tháng không đúng định dạng YYYY-MM", 400)
        year, mon = month.split('-')
        query = query.filter(
            db.extract('year', TeachingSession.date) == int(year),
            db.extract('month', TeachingSession.date) == int(mon)
        )
    if teacher_id:
        query = query.filter_by(teacher_id=int(teacher_id))
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    sessions = query.order_by(TeachingSession.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return paginated_response(
        items=[s.to_dict() for s in sessions.items],
        total=total, page=page, per_page=per_page
    )


@admin_bp.route('/sessions', methods=['POST'])
@admin_required
def create_session():
    data = request.get_json()
    errors = validate_required(data, ['teacher_id', 'salary_rate_id', 'date', 'shift'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if not validate_date_format(data['date']):
        return error_response("Ngày không đúng định dạng YYYY-MM-DD", 400)
    if not validate_shift(data['shift']):
        return error_response("Ca dạy phải là: morning, afternoon, evening", 400)

    teacher = User.query.get(data['teacher_id'])
    if not teacher or teacher.role != 'teacher':
        return error_response("Giáo viên không tồn tại", 404)

    salary_rate = SalaryRate.query.get(data['salary_rate_id'])
    if not salary_rate or not salary_rate.is_active:
        return error_response("Mệnh giá không tồn tại", 404)

    # Kiểm tra trùng lịch
    existing = TeachingSession.query.filter_by(
        teacher_id=data['teacher_id'],
        date=data['date'],
        shift=data['shift']
    ).first()
    if existing:
        return error_response("Giáo viên đã có lịch dạy ca này", 409)

    from datetime import date as dt_date
    session = TeachingSession(
        teacher_id=data['teacher_id'],
        salary_rate_id=data['salary_rate_id'],
        date=dt_date.fromisoformat(data['date']),
        shift=data['shift'],
        note=data.get('note', '')
    )
    db.session.add(session)
    db.session.commit()

    return success_response(session.to_dict(), "Tạo buổi dạy thành công", 201)


@admin_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@admin_required
def update_session(session_id):
    session = TeachingSession.query.get(session_id)
    if not session:
        return error_response("Buổi dạy không tồn tại", 404)

    data = request.get_json()
    if 'status' in data and data['status'] in ['pending', 'confirmed', 'cancelled']:
        session.status = data['status']
    if 'note' in data:
        session.note = data['note']
    if 'salary_rate_id' in data:
        session.salary_rate_id = data['salary_rate_id']

    db.session.commit()
    return success_response(session.to_dict(), "Cập nhật thành công")


@admin_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@admin_required
def delete_session(session_id):
    session = TeachingSession.query.get(session_id)
    if not session:
        return error_response("Buổi dạy không tồn tại", 404)

    session.status = 'cancelled'
    db.session.commit()
    return success_response(message="Đã huỷ buổi dạy")


# ─── QUẢN LÝ MỆNH GIÁ ────────────────────────────────────────────────────────

@admin_bp.route('/salary-rates', methods=['GET'])
@admin_required
def get_salary_rates():
    rates = SalaryRate.query.filter_by(is_active=True).all()
    return success_response([r.to_dict() for r in rates])


@admin_bp.route('/salary-rates', methods=['POST'])
@admin_required
def create_salary_rate():
    data = request.get_json()
    errors = validate_required(data, ['class_type', 'amount'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    try:
        amount = int(data['amount'])
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return error_response("Số tiền phải là số nguyên dương", 400)

    rate = SalaryRate(
        class_type=data['class_type'].strip(),
        amount=amount,
        description=data.get('description', '')
    )
    db.session.add(rate)
    db.session.commit()

    return success_response(rate.to_dict(), "Tạo mệnh giá thành công", 201)


@admin_bp.route('/salary-rates/<int:rate_id>', methods=['PUT'])
@admin_required
def update_salary_rate(rate_id):
    rate = SalaryRate.query.get(rate_id)
    if not rate:
        return error_response("Mệnh giá không tồn tại", 404)

    data = request.get_json()
    if 'class_type' in data:
        rate.class_type = data['class_type'].strip()
    if 'amount' in data:
        rate.amount = int(data['amount'])
    if 'description' in data:
        rate.description = data['description']
    if 'is_active' in data:
        rate.is_active = bool(data['is_active'])

    db.session.commit()
    return success_response(rate.to_dict(), "Cập nhật thành công")


# ─── BÁO CÁO LƯƠNG ───────────────────────────────────────────────────────────

@admin_bp.route('/salary/report', methods=['GET'])
@admin_required
def salary_report():
    month = request.args.get('month')
    if not month or not validate_month_format(month):
        return error_response("Vui lòng truyền tháng đúng định dạng YYYY-MM", 400)

    year, mon = month.split('-')

    # Query tổng hợp
    results = db.session.query(
        User.id,
        User.full_name,
        User.employee_id,
        func.count(TeachingSession.id).label('total_sessions'),
        func.sum(SalaryRate.amount).label('total_salary')
    ).join(TeachingSession, TeachingSession.teacher_id == User.id)\
     .join(SalaryRate, SalaryRate.id == TeachingSession.salary_rate_id)\
     .filter(
        TeachingSession.status == 'confirmed',
        db.extract('year', TeachingSession.date) == int(year),
        db.extract('month', TeachingSession.date) == int(mon)
     ).group_by(User.id, User.full_name, User.employee_id)\
      .all()

    data = [{
        "teacher_id":     r.id,
        "employee_id":    r.employee_id,
        "full_name":      r.full_name,
        "total_sessions": r.total_sessions,
        "total_salary":   int(r.total_salary or 0)
    } for r in results]

    return success_response({
        "month":   month,
        "teachers": data,
        "summary": {
            "total_teachers": len(data),
            "total_sessions": sum(r['total_sessions'] for r in data),
            "total_salary":   sum(r['total_salary'] for r in data)
        }
    })


# ─── QUẢN LÝ HỌC SINH ────────────────────────────────────────────────────────

@admin_bp.route('/students', methods=['GET'])
@admin_required
def get_students():
    class_name = request.args.get('class_name')
    query = Student.query.filter_by(is_active=True)
    if class_name:
        query = query.filter_by(class_name=class_name)
    students = query.order_by(Student.name).all()
    return success_response([s.to_dict() for s in students])


@admin_bp.route('/students', methods=['POST'])
@admin_required
def create_student():
    data = request.get_json()
    errors = validate_required(data, ['name'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    student = Student(
        name=data['name'].strip(),
        class_name=data.get('class_name', ''),
        phone=data.get('phone', ''),
        note=data.get('note', '')
    )
    db.session.add(student)
    db.session.commit()

    return success_response(student.to_dict(), "Thêm học sinh thành công", 201)


@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return error_response("Học sinh không tồn tại", 404)

    data = request.get_json()
    if 'name' in data:
        student.name = data['name'].strip()
    if 'class_name' in data:
        student.class_name = data['class_name']
    if 'phone' in data:
        student.phone = data['phone']
    if 'note' in data:
        student.note = data['note']
    if 'is_active' in data:
        student.is_active = bool(data['is_active'])

    db.session.commit()
    return success_response(student.to_dict(), "Cập nhật thành công")