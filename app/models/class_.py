from datetime import datetime, date
from app.extensions import db


class Class(db.Model):
    __tablename__ = 'classes'

    id               = db.Column(db.Integer, primary_key=True)
    subject_id       = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id       = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    room_id          = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    class_name       = db.Column(db.String(100), nullable=False)
    class_code       = db.Column(db.String(20), unique=True, nullable=True)
    max_students     = db.Column(db.Integer, default=15)
    current_students = db.Column(db.Integer, default=0)
    start_date       = db.Column(db.Date, nullable=False)
    end_date         = db.Column(db.Date, nullable=True)
    # Ngày trong tuần: "2,4,6" = T2, T4, T6
    schedule_days    = db.Column(db.String(20), nullable=True)
    schedule_time    = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, default=90)
    status           = db.Column(
        db.Enum('active', 'completed', 'cancelled', name='class_status'),
        default='active', nullable=False
    )
    notes            = db.Column(db.Text, nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subject  = db.relationship('Subject', backref='classes')
    teacher  = db.relationship('Teacher', backref='classes')
    room     = db.relationship('Room', backref='classes')

    def get_formatted_schedule(self):
        schedule_templates = getattr(self, 'schedule_templates', None)
        if not schedule_templates:
            return "Chưa xếp lịch"
        
        from collections import defaultdict
        groups = defaultdict(list)
        for tpl in schedule_templates:
            start_str = tpl.start_time.strftime('%H:%M') if getattr(tpl, 'start_time', None) else ''
            end_str = tpl.end_time.strftime('%H:%M') if getattr(tpl, 'end_time', None) else ''
            time_key = (start_str, end_str)
            groups[time_key].append(tpl.day_of_week)
            
        day_map = {0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "CN"}
        parts = []
        for (start, end), days in groups.items():
            days.sort()
            days_str = ",".join(day_map.get(d, str(d)) for d in days)
            format_time = start
            if start:
                h, m = start.split(':')
                if m == '00':
                    format_time = f"{int(h)}h"
                else:
                    format_time = f"{int(h)}h{m}"
            
            parts.append(f"{days_str} - {format_time}")
            
        return " và ".join(parts)

    def to_dict(self, include_relations=True, include_students=False):
        formatted_sched = self.get_formatted_schedule()
        data = {
            "id":               self.id,
            "class_name":       self.class_name,
            "class_code":       self.class_code,
            "subject_id":       self.subject_id,
            "teacher_id":       self.teacher_id,
            "room_id":          self.room_id,
            "max_students":     self.max_students,
            "current_students": self.current_students,
            "start_date":       self.start_date.isoformat() if self.start_date else None,
            "end_date":         self.end_date.isoformat() if self.end_date else None,
            "schedule_days":    self.schedule_days,
            "schedule_time":    self.schedule_time.strftime('%H:%M') if self.schedule_time else None,
            "formatted_schedule": formatted_sched,
            "duration_minutes": self.duration_minutes,
            "status":           self.status,
            "notes":            self.notes,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
        }
        if include_relations:
            data["subject"] = {
                "id":   self.subject.id,
                "name": self.subject.subject_name,
                "code": self.subject.subject_code,
                "fee_per_session": float(self.subject.fee_per_session),
            } if self.subject else None
            data["teacher"] = {
                "id":           self.teacher.id,
                "teacher_code": self.teacher.teacher_code,
                "full_name":    self.teacher.full_name,
            } if self.teacher else None
            data["room"] = {
                "id":        self.room.id,
                "room_name": self.room.room_name,
            } if self.room else None

        if include_students:
            active_students = []
            for enrollment in getattr(self, 'enrollments', []):
                if enrollment.status == 'active' and getattr(enrollment, 'student', None):
                    active_students.append({
                        "student_id": enrollment.student.id,
                        "full_name":  enrollment.student.full_name,
                        "schedule": formatted_sched
                    })
            data["students"] = active_students

        return data
