from datetime import date
from flask import Blueprint, request
from sqlalchemy import func
from app.extensions import db
from app.models.monthly_fee import MonthlyFee
from app.models.student_attendance import StudentAttendance
from app.models.schedule import Schedule
from app.models.student_class import StudentClass
from app.models.class_ import Class
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_month_format

monthly_fees_bp = Blueprint('admin_monthly_fees', __name__)


@monthly_fees_bp.route('', methods=['GET'])
@admin_required
def get_monthly_fees():
    month_year = request.args.get('month_year')
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    status = request.args.get('status')

    query = MonthlyFee.query
    if month_year:
        query = query.filter_by(month_year=month_year)
    if student_id:
        query = query.filter_by(student_id=int(student_id))
    if class_id:
        query = query.filter_by(class_id=int(class_id))
    if status:
        query = query.filter_by(status=status)

    fees = query.order_by(MonthlyFee.month_year.desc()).all()
    return success_response([f.to_dict() for f in fees])


@monthly_fees_bp.route('/generate', methods=['POST'])
@admin_required
def generate_monthly_fees():
    """
    Tính học phí tháng.
    billable = attended + excused_absences
    Không tính: unexcused_absences + teacher_cancelled
    """
    data = request.get_json() or {}
    month_year = data.get('month_year')
    if not month_year or not validate_month_format(month_year):
        return error_response("Vui lòng truyền month_year đúng định dạng YYYY-MM", 400)

    year, month = month_year.split('-')

    # Lấy tất cả lịch trong tháng
    schedules_in_month = Schedule.query.filter(
        db.extract('year',  Schedule.schedule_date) == int(year),
        db.extract('month', Schedule.schedule_date) == int(month),
        Schedule.status.in_(['completed', 'scheduled'])
    ).all()

    class_ids = list({s.class_id for s in schedules_in_month})
    created_count = 0
    updated_count = 0

    for class_id in class_ids:
        cls = Class.query.get(class_id)
        if not cls:
            continue

        total_sessions = len([s for s in schedules_in_month if s.class_id == class_id])
        enrollments = StudentClass.query.filter_by(class_id=class_id, status='active').all()

        for enr in enrollments:
            # Đếm theo từng loại status
            att_counts = db.session.query(
                StudentAttendance.status, func.count(StudentAttendance.id)
            ).filter(
                StudentAttendance.student_id == enr.student_id,
                StudentAttendance.class_id == class_id,
                db.extract('year',  StudentAttendance.attendance_date) == int(year),
                db.extract('month', StudentAttendance.attendance_date) == int(month),
            ).group_by(StudentAttendance.status).all()

            counts = {row[0]: row[1] for row in att_counts}
            attended     = counts.get('present', 0)
            excused      = counts.get('absent_excused', 0)
            unexcused    = counts.get('absent_unexcused', 0)
            t_cancelled  = counts.get('teacher_cancelled', 0)
            billable     = attended + excused

            fee_per_session = float(enr.final_fee)
            total_amount    = fee_per_session * billable
            final_amount    = total_amount  # Có thể thêm discount logic ở đây

            existing = MonthlyFee.query.filter_by(
                student_id=enr.student_id, class_id=class_id, month_year=month_year
            ).first()

            if existing:
                existing.total_sessions     = total_sessions
                existing.attended_sessions  = attended
                existing.excused_absences   = excused
                existing.unexcused_absences = unexcused
                existing.teacher_cancelled  = t_cancelled
                existing.billable_sessions  = billable
                existing.fee_per_session    = fee_per_session
                existing.total_amount       = total_amount
                existing.final_amount       = final_amount
                updated_count += 1
            else:
                fee = MonthlyFee(
                    student_id=enr.student_id,
                    class_id=class_id,
                    month_year=month_year,
                    total_sessions=total_sessions,
                    attended_sessions=attended,
                    excused_absences=excused,
                    unexcused_absences=unexcused,
                    teacher_cancelled=t_cancelled,
                    billable_sessions=billable,
                    fee_per_session=fee_per_session,
                    total_amount=total_amount,
                    final_amount=final_amount,
                    status='draft',
                )
                db.session.add(fee)
                created_count += 1

    db.session.commit()
    return success_response({
        "month_year": month_year,
        "created": created_count,
        "updated": updated_count,
    }, "Tính học phí thành công")


@monthly_fees_bp.route('/<int:fee_id>/confirm', methods=['PUT'])
@admin_required
def confirm_fee(fee_id):
    fee = MonthlyFee.query.get(fee_id)
    if not fee:
        return error_response("Hoá đơn không tồn tại", 404)
    if fee.status != 'draft':
        return error_response("Chỉ có thể xác nhận hoá đơn ở trạng thái draft", 400)
    fee.status = 'confirmed'
    db.session.commit()
    return success_response(fee.to_dict(), "Đã xác nhận hoá đơn học phí")


@monthly_fees_bp.route('/<int:fee_id>', methods=['GET'])
@admin_required
def get_fee(fee_id):
    fee = MonthlyFee.query.get(fee_id)
    if not fee:
        return error_response("Hoá đơn không tồn tại", 404)
    return success_response(fee.to_dict())
