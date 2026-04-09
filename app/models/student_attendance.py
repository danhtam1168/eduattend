from datetime import datetime
from app.extensions import db


class StudentAttendance(db.Model):
    """Điểm danh học sinh — linked to teacher_attendances"""
    __tablename__ = 'student_attendances'

    id                   = db.Column(db.Integer, primary_key=True)
    student_id           = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id             = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_attendance_id = db.Column(db.Integer, db.ForeignKey('teacher_attendances.id'), nullable=False)
    attendance_date      = db.Column(db.Date, nullable=False)
    session_count        = db.Column(db.Integer, default=1)
    status               = db.Column(
        db.Enum(
            'present',
            'absent_excused',       # Vắng có phép
            'absent_unexcused',     # Vắng không phép
            'teacher_cancelled',    # GV huỷ buổi
            name='student_attendance_status'
        ),
        nullable=False
    )
    notes                = db.Column(db.Text, nullable=True)
    teacher_id           = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique: 1 học sinh / 1 lớp / 1 ngày
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', 'attendance_date', name='uq_student_class_date'),
    )

    # Relationships
    student             = db.relationship('Student', backref='attendances')
    class_              = db.relationship('Class', backref='student_attendances')
    teacher_attendance  = db.relationship('TeacherAttendance', backref='student_attendances')
    teacher             = db.relationship('Teacher', backref='marked_attendances')

    def to_dict(self):
        return {
            "id":                    self.id,
            "student_id":            self.student_id,
            "class_id":              self.class_id,
            "teacher_attendance_id": self.teacher_attendance_id,
            "attendance_date":       self.attendance_date.isoformat() if self.attendance_date else None,
            "session_count":         self.session_count,
            "status":                self.status,
            "notes":                 self.notes,
            "student": {
                "id":        self.student.id,
                "full_name": self.student.full_name,
                "student_code": self.student.student_code,
            } if self.student else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
