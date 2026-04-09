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

    def to_dict(self, include_relations=True):
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
        return data
