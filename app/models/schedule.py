from datetime import datetime
from app.extensions import db


class Schedule(db.Model):
    __tablename__ = 'schedules'

    id            = db.Column(db.Integer, primary_key=True)
    class_id      = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id    = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    schedule_date = db.Column(db.Date, nullable=False)
    start_time    = db.Column(db.Time, nullable=False)
    end_time      = db.Column(db.Time, nullable=False)
    status        = db.Column(
        db.Enum('scheduled', 'completed', 'cancelled', 'rescheduled', name='schedule_status'),
        default='scheduled', nullable=False
    )
    room_id       = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    notes         = db.Column(db.Text, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique: 1 lớp chỉ có 1 lịch trong 1 ngày
    __table_args__ = (
        db.UniqueConstraint('class_id', 'schedule_date', name='uq_class_date'),
    )

    # Relationships
    class_   = db.relationship('Class', backref='schedules')
    teacher  = db.relationship('Teacher', backref='schedules')
    room     = db.relationship('Room', backref='schedules')

    def to_dict(self, include_relations=True):
        data = {
            "id":            self.id,
            "class_id":      self.class_id,
            "teacher_id":    self.teacher_id,
            "schedule_date": self.schedule_date.isoformat() if self.schedule_date else None,
            "start_time":    self.start_time.strftime('%H:%M') if self.start_time else None,
            "end_time":      self.end_time.strftime('%H:%M') if self.end_time else None,
            "status":        self.status,
            "room_id":       self.room_id,
            "notes":         self.notes,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
        }
        if include_relations:
            data["class_"]  = {"id": self.class_.id, "class_name": self.class_.class_name} if self.class_ else None
            data["teacher"] = {"id": self.teacher.id, "full_name": self.teacher.full_name} if self.teacher else None
            data["room"]    = {"id": self.room.id, "room_name": self.room.room_name} if self.room else None
        return data
