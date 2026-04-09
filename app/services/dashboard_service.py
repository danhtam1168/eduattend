from datetime import date
from sqlalchemy import func
from app.extensions import db
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.class_ import Class
from app.models.schedule import Schedule
from app.models.teacher_attendance import TeacherAttendance
from app.models.monthly_fee import MonthlyFee
from app.models.payment import Payment

class DashboardService:
    @staticmethod
    def get_dashboard_stats():
        today = date.today()

        total_teachers = Teacher.query.filter_by(status='active').count()
        pending_teachers = Teacher.query.filter_by(status='pending').count()
        total_students = Student.query.filter_by(is_active=True, status='active').count()
        total_classes = Class.query.filter_by(status='active').count()

        today_schedules = Schedule.query.filter_by(schedule_date=today).count()

        sessions_this_month = TeacherAttendance.query.filter(
            db.extract('year',  TeacherAttendance.attendance_date) == today.year,
            db.extract('month', TeacherAttendance.attendance_date) == today.month,
            TeacherAttendance.status == 'present'
        ).count()

        fee_revenue = db.session.query(
            func.sum(Payment.amount)
        ).filter(
            db.extract('year',  Payment.payment_date) == today.year,
            db.extract('month', Payment.payment_date) == today.month,
            Payment.status == 'completed'
        ).scalar() or 0

        overdue_fees = MonthlyFee.query.filter_by(status='overdue').count()

        return {
            "teachers": {
                "total":   total_teachers,
                "pending": pending_teachers,
            },
            "students": {
                "total": total_students,
            },
            "classes": {
                "total": total_classes,
            },
            "today": {
                "schedules": today_schedules,
            },
            "this_month": {
                "sessions":      sessions_this_month,
                "fee_revenue":   float(fee_revenue),
                "overdue_fees":  overdue_fees,
            }
        }
