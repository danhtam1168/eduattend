from datetime import date, datetime
from flask import Blueprint, request
from sqlalchemy import func
from app.extensions import db
from app.models.teacher_salary import TeacherSalary
from app.models.teacher_attendance import TeacherAttendance
from app.models.teacher import Teacher
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required, get_current_admin
from app.utils.validators import validate_month_format

teacher_salaries_bp = Blueprint('admin_teacher_salaries', __name__)


@teacher_salaries_bp.route('', methods=['GET'])
@admin_required
def get_salaries():
    month_year = request.args.get('month_year')
    status = request.args.get('status')

    query = TeacherSalary.query
    if month_year:
        query = query.filter_by(month_year=month_year)
    if status:
        query = query.filter_by(status=status)

    salaries = query.order_by(TeacherSalary.month_year.desc()).all()
    return success_response([s.to_dict() for s in salaries])


@teacher_salaries_bp.route('/generate', methods=['POST'])
@admin_required
def generate_salaries():
    """Tính lương tháng dựa trên teacher_attendances"""
    data = request.get_json() or {}
    month_year = data.get('month_year')
    if not month_year or not validate_month_format(month_year):
        return error_response("Vui lòng truyền month_year đúng định dạng YYYY-MM", 400)

    year, month = month_year.split('-')

    # Tổng hợp số buổi theo giáo viên
    results = db.session.query(
        TeacherAttendance.teacher_id,
        func.sum(TeacherAttendance.session_count).label('total_sessions')
    ).filter(
        db.extract('year',  TeacherAttendance.attendance_date) == int(year),
        db.extract('month', TeacherAttendance.attendance_date) == int(month),
        TeacherAttendance.status == 'present'
    ).group_by(TeacherAttendance.teacher_id).all()

    created_count = 0
    updated_count = 0

    for teacher_id, total_sessions in results:
        teacher = Teacher.query.get(teacher_id)
        if not teacher or not teacher.rate_per_session:
            continue

        rate = float(teacher.rate_per_session)
        sessions = float(total_sessions)
        base_salary = rate * sessions
        net_salary = base_salary  # Bonus/deduction có thể điều chỉnh thủ công

        existing = TeacherSalary.query.filter_by(
            teacher_id=teacher_id, month_year=month_year
        ).first()

        if existing:
            if existing.status == 'draft':
                existing.total_sessions = sessions
                existing.rate_per_session = rate
                existing.base_salary = base_salary
                existing.net_salary = net_salary
            updated_count += 1
        else:
            salary = TeacherSalary(
                teacher_id=teacher_id,
                month_year=month_year,
                total_sessions=sessions,
                rate_per_session=rate,
                base_salary=base_salary,
                net_salary=net_salary,
                status='draft',
            )
            db.session.add(salary)
            created_count += 1

    db.session.commit()
    return success_response({"created": created_count, "updated": updated_count},
                            "Tính lương thành công")


@teacher_salaries_bp.route('/<int:salary_id>', methods=['PUT'])
@admin_required
def update_salary(salary_id):
    salary = TeacherSalary.query.get(salary_id)
    if not salary:
        return error_response("Bản ghi lương không tồn tại", 404)

    data = request.get_json()
    editable = ['bonus', 'deduction', 'advance_payment', 'notes']
    for field in editable:
        if field in data:
            setattr(salary, field, float(data[field]))

    # Tính lại net_salary
    salary.net_salary = float(salary.base_salary) + float(salary.bonus) - float(salary.deduction) - float(salary.advance_payment)
    db.session.commit()
    return success_response(salary.to_dict(), "Cập nhật thành công")


@teacher_salaries_bp.route('/<int:salary_id>/approve', methods=['PUT'])
@admin_required
def approve_salary(salary_id):
    salary = TeacherSalary.query.get(salary_id)
    if not salary:
        return error_response("Bản ghi lương không tồn tại", 404)
    if salary.status != 'draft':
        return error_response("Chỉ có thể phê duyệt bảng lương ở trạng thái draft", 400)

    admin = get_current_admin()
    salary.status = 'approved'
    salary.approved_by = admin.id
    db.session.commit()
    return success_response(salary.to_dict(), "Đã phê duyệt bảng lương")


@teacher_salaries_bp.route('/<int:salary_id>/pay', methods=['PUT'])
@admin_required
def pay_salary(salary_id):
    salary = TeacherSalary.query.get(salary_id)
    if not salary:
        return error_response("Bản ghi lương không tồn tại", 404)
    if salary.status != 'approved':
        return error_response("Bảng lương phải được phê duyệt trước khi thanh toán", 400)

    admin = get_current_admin()
    salary.status = 'paid'
    salary.payment_date = date.today()
    salary.paid_by = admin.id
    db.session.commit()
    return success_response(salary.to_dict(), "Đã ghi nhận thanh toán lương")
