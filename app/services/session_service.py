from datetime import date
from app.extensions import db
from app.models.schedule import Schedule
from app.models.teacher_attendance import TeacherAttendance
from app.utils.validators import validate_month_format

class SessionService:
    @staticmethod
    def get_teacher_schedule(teacher_id, month, from_date, to_date):
        query = Schedule.query.filter_by(teacher_id=teacher_id)

        if month:
            if not validate_month_format(month):
                raise ValueError("Tháng không đúng định dạng YYYY-MM")
            year, mon = month.split('-')
            query = query.filter(
                db.extract('year',  Schedule.schedule_date) == int(year),
                db.extract('month', Schedule.schedule_date) == int(mon),
            )
        if from_date:
            query = query.filter(Schedule.schedule_date >= date.fromisoformat(from_date))
        if to_date:
            query = query.filter(Schedule.schedule_date <= date.fromisoformat(to_date))

        schedules = query.order_by(Schedule.schedule_date.asc()).all()
        results = []
        for s in schedules:
            d = s.to_dict()
            att = TeacherAttendance.query.filter_by(
                teacher_id=teacher_id, class_id=s.class_id, attendance_date=s.schedule_date
            ).first()
            d['teacher_attendance'] = att.to_dict(include_relations=False) if att else None
            results.append(d)
        return results

    @staticmethod
    def get_today_schedule(teacher_id):
        today = date.today()
        schedules = Schedule.query.filter_by(teacher_id=teacher_id, schedule_date=today).all()
        results = []
        for s in schedules:
            d = s.to_dict()
            att = TeacherAttendance.query.filter_by(
                teacher_id=teacher_id, class_id=s.class_id, attendance_date=today
            ).first()
            d['teacher_attendance'] = att.to_dict(include_relations=False) if att else None
            results.append(d)
        return results

    @staticmethod
    def checkin(teacher_id, data):
        class_id = data.get('class_id')
        att_date = data.get('attendance_date', date.today().isoformat())

        if not class_id:
            raise ValueError("Vui lòng cung cấp class_id")

        existing = TeacherAttendance.query.filter_by(
            teacher_id=teacher_id, class_id=int(class_id), attendance_date=att_date
        ).first()
        if existing:
            raise ValueError("Bạn đã chấm công buổi này rồi")

        sched = Schedule.query.filter_by(class_id=int(class_id), schedule_date=att_date).first()
        if not sched:
            raise ValueError("Không tìm thấy lịch dạy cho lớp này trong ngày")
        if sched.teacher_id != teacher_id:
            raise ValueError("Đây không phải lịch dạy của bạn")

        att = TeacherAttendance(
            teacher_id=teacher_id,
            class_id=int(class_id),
            schedule_id=sched.id,
            attendance_date=date.fromisoformat(att_date),
            session_count=float(data.get('session_count', 1)),
            status='present',
            notes=data.get('notes', ''),
        )
        db.session.add(att)
        db.session.commit()
        return att
