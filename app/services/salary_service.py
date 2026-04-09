from datetime import date
from sqlalchemy import func
from app.extensions import db
from app.models.teacher_salary import TeacherSalary
from app.models.teacher_attendance import TeacherAttendance
from app.models.teacher import Teacher
from app.utils.validators import validate_month_format

class SalaryService:
    @staticmethod
    def get_salaries(month_year, status):
        query = TeacherSalary.query
        if month_year:
            query = query.filter_by(month_year=month_year)
        if status:
            query = query.filter_by(status=status)

        return query.order_by(TeacherSalary.month_year.desc()).all()

    @staticmethod
    def generate_salaries(month_year):
        if not month_year or not validate_month_format(month_year):
            raise ValueError("Vui lòng truyền month_year đúng định dạng YYYY-MM")

        year, month = month_year.split('-')

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
            net_salary = base_salary

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
        return created_count, updated_count

    @staticmethod
    def update_salary(salary_id, data):
        salary = TeacherSalary.query.get(salary_id)
        if not salary:
            raise ValueError("Bản ghi lương không tồn tại")

        editable = ['bonus', 'deduction', 'advance_payment', 'notes']
        for field in editable:
            if field in data:
                setattr(salary, field, float(data[field]))

        salary.net_salary = float(salary.base_salary) + float(salary.bonus) - float(salary.deduction) - float(salary.advance_payment)
        db.session.commit()
        return salary

    @staticmethod
    def approve_salary(salary_id, admin_id):
        salary = TeacherSalary.query.get(salary_id)
        if not salary:
            raise ValueError("Bản ghi lương không tồn tại")
        if salary.status != 'draft':
            raise ValueError("Chỉ có thể phê duyệt bảng lương ở trạng thái draft")

        salary.status = 'approved'
        salary.approved_by = admin_id
        db.session.commit()
        return salary

    @staticmethod
    def pay_salary(salary_id, admin_id):
        salary = TeacherSalary.query.get(salary_id)
        if not salary:
            raise ValueError("Bản ghi lương không tồn tại")
        if salary.status != 'approved':
            raise ValueError("Bảng lương phải được phê duyệt trước khi thanh toán")

        salary.status = 'paid'
        salary.payment_date = date.today()
        salary.paid_by = admin_id
        db.session.commit()
        return salary
