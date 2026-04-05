from datetime import datetime
from app.extensions import db


class StudentAttendance(db.Model):
    __tablename__ = 'student_attendances'

    id          = db.Column(db.Integer, primary_key=True)
    session_id  = db.Column(db.Integer, db.ForeignKey('teaching_sessions.id'), nullable=False)
    student_id  = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    is_present  = db.Column(db.Boolean, default=False, nullable=False)
    note        = db.Column(db.String(255), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student     = db.relationship('Student', backref='attendances')

    # Không cho điểm danh trùng (1 học sinh / 1 buổi)
    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='uq_session_student'),
    )

    def to_dict(self):
        return {
            "id":         self.id,
            "session_id": self.session_id,
            "is_present": self.is_present,
            "note":       self.note,
            "student": {
                "id":         self.student.id,
                "name":       self.student.name,
                "class_name": self.student.class_name,
            }
        }