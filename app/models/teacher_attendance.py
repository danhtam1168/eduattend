from datetime import datetime
from app.extensions import db


class TeacherAttendance(db.Model):
    """Chấm công giáo viên — PHẢI chấm trước khi điểm danh học sinh"""
    __tablename__ = 'teacher_attendances'

    id              = db.Column(db.Integer, primary_key=True)
    teacher_id      = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    class_id        = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    schedule_id     = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=True)
    attendance_date = db.Column(db.Date, nullable=False)
    session_count   = db.Column(db.Numeric(4, 1), default=1)  # Hỗ trợ nửa buổi: 0.5, 1.0
    status          = db.Column(
        db.Enum('present', 'absent', 'late', 'early_leave', name='teacher_attendance_status'),
        default='present', nullable=False
    )
    notes           = db.Column(db.Text, nullable=True)
    recorded_by     = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique: 1 giáo viên / 1 lớp / 1 ngày
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'class_id', 'attendance_date', name='uq_teacher_class_date'),
    )

    # Relationships
    teacher  = db.relationship('Teacher', backref='teacher_attendances')
    class_   = db.relationship('Class', backref='teacher_attendances')
    schedule = db.relationship('Schedule', backref='teacher_attendance', uselist=False)
    recorder = db.relationship('Admin', backref='recorded_attendances')

    def to_dict(self, include_relations=True):
        data = {
            "id":              self.id,
            "teacher_id":      self.teacher_id,
            "class_id":        self.class_id,
            "schedule_id":     self.schedule_id,
            "attendance_date": self.attendance_date.isoformat() if self.attendance_date else None,
            "session_count":   float(self.session_count),
            "status":          self.status,
            "notes":           self.notes,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
        }
        if include_relations:
            data["teacher"] = {
                "id":           self.teacher.id,
                "teacher_code": self.teacher.teacher_code,
                "full_name":    self.teacher.full_name,
            } if self.teacher else None
            data["class_"] = {
                "id":         self.class_.id,
                "class_name": self.class_.class_name,
            } if self.class_ else None
        return data
