from datetime import date, time
from app.extensions import db
from app.models.schedule import Schedule
from app.models.class_ import Class

class ScheduleService:
    @staticmethod
    def get_schedules(class_id, teacher_id, from_date, to_date, status):
        query = Schedule.query
        if class_id:
            query = query.filter_by(class_id=int(class_id))
        if teacher_id:
            query = query.filter_by(teacher_id=int(teacher_id))
        if from_date:
            query = query.filter(Schedule.schedule_date >= date.fromisoformat(from_date))
        if to_date:
            query = query.filter(Schedule.schedule_date <= date.fromisoformat(to_date))
        if status:
            query = query.filter_by(status=status)

        return query.order_by(Schedule.schedule_date.desc()).all()

    @staticmethod
    def create_schedule(data):
        cls = Class.query.get(int(data['class_id']))
        if not cls or cls.status != 'active':
            raise ValueError("Lớp học không tồn tại hoặc không còn hoạt động")

        if Schedule.query.filter_by(class_id=cls.id, schedule_date=data['schedule_date']).first():
            raise ValueError("Lớp học đã có lịch trong ngày này")

        sched = Schedule(
            class_id=cls.id,
            teacher_id=data.get('teacher_id', cls.teacher_id),
            schedule_date=date.fromisoformat(data['schedule_date']),
            start_time=time.fromisoformat(data['start_time']),
            end_time=time.fromisoformat(data['end_time']),
            room_id=data.get('room_id', cls.room_id),
            notes=data.get('notes', ''),
        )
        db.session.add(sched)
        db.session.commit()
        return sched

    @staticmethod
    def update_schedule(schedule_id, data):
        sched = Schedule.query.get(schedule_id)
        if not sched:
            raise ValueError("Lịch học không tồn tại")

        editable = ['start_time', 'end_time', 'room_id', 'status', 'notes', 'teacher_id']
        for field in editable:
            if field in data:
                setattr(sched, field, data[field])

        db.session.commit()
        return sched

    @staticmethod
    def cancel_schedule(schedule_id):
        sched = Schedule.query.get(schedule_id)
        if not sched:
            raise ValueError("Lịch học không tồn tại")
        sched.status = 'cancelled'
        db.session.commit()
