from sqlalchemy import func
from app.extensions import db
from app.models.monthly_fee import MonthlyFee
from app.models.student_attendance import StudentAttendance
from app.models.schedule import Schedule
from app.models.student_class import StudentClass
from app.models.class_ import Class
from app.utils.validators import validate_month_format

class MonthlyFeeService:
    @staticmethod
    def get_monthly_fees(month_year, student_id, class_id, status):
        query = MonthlyFee.query
        if month_year:
            query = query.filter_by(month_year=month_year)
        if student_id:
            query = query.filter_by(student_id=int(student_id))
        if class_id:
            query = query.filter_by(class_id=int(class_id))
        if status:
            query = query.filter_by(status=status)

        return query.order_by(MonthlyFee.month_year.desc()).all()

    @staticmethod
    def generate_monthly_fees(month_year):
        if not month_year or not validate_month_format(month_year):
            raise ValueError("Vui lòng truyền month_year đúng định dạng YYYY-MM")

        year, month = month_year.split('-')

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
                final_amount    = total_amount

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
        return created_count, updated_count

    @staticmethod
    def confirm_fee(fee_id):
        fee = MonthlyFee.query.get(fee_id)
        if not fee:
            raise ValueError("Hoá đơn không tồn tại")
        if fee.status != 'draft':
            raise ValueError("Chỉ có thể xác nhận hoá đơn ở trạng thái draft")
        fee.status = 'confirmed'
        db.session.commit()
        return fee

    @staticmethod
    def get_fee(fee_id):
        fee = MonthlyFee.query.get(fee_id)
        if not fee:
            raise ValueError("Hoá đơn không tồn tại")
        return fee
