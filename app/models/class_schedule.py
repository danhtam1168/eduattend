from datetime import datetime
from app.extensions import db

class ClassSchedule(db.Model):
    """Mô hình lưu trữ Khung thời khóa biểu (Mẫu cố định) của một lớp học"""
    __tablename__ = 'class_schedules'

    id          = db.Column(db.Integer, primary_key=True)
    class_id    = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    # day_of_week: 0 = Thứ 2, 1 = Thứ 3, ..., 6 = Chủ nhật
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time  = db.Column(db.Time, nullable=False)
    end_time    = db.Column(db.Time, nullable=False)
    room_id     = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    class_ = db.relationship('Class', backref=db.backref('schedule_templates', cascade='all, delete-orphan'))
    room   = db.relationship('Room')

    def to_dict(self):
        return {
            "id":          self.id,
            "class_id":    self.class_id,
            "day_of_week": self.day_of_week,
            "start_time":  self.start_time.strftime('%H:%M') if self.start_time else None,
            "end_time":    self.end_time.strftime('%H:%M') if self.end_time else None,
            "room_id":     self.room_id,
            "room":        {"id": self.room.id, "room_name": self.room.room_name} if self.room else None,
            "class_name":  self.class_.class_name if self.class_ else None,
            "teacher_name":self.class_.teacher.full_name if self.class_ and self.class_.teacher else None
        }
