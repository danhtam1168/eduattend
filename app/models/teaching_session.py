from datetime import datetime
from app.extensions import db


class TeachingSession(db.Model):
    __tablename__ = 'teaching_sessions'

    id             = db.Column(db.Integer, primary_key=True)
    teacher_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salary_rate_id = db.Column(db.Integer, db.ForeignKey('salary_rates.id'), nullable=False)
    date           = db.Column(db.Date, nullable=False)
    shift          = db.Column(db.Enum('morning', 'afternoon', 'evening', name='shift_enum'), nullable=False)
    status         = db.Column(db.Enum('pending', 'confirmed', 'cancelled', name='session_status'), default='pending', nullable=False)
    confirmed_at   = db.Column(db.DateTime, nullable=True)
    note           = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher        = db.relationship('User', backref='sessions')
    salary_rate    = db.relationship('SalaryRate', backref='sessions')
    attendances    = db.relationship('StudentAttendance', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_attendances=False):
        data = {
            "id":           self.id,
            "date":         self.date.isoformat() if self.date else None,
            "shift":        self.shift,
            "status":       self.status,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "note":         self.note,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
            "teacher": {
                "id":       self.teacher.id,
                "name":     self.teacher.full_name,
                "employee_id": self.teacher.employee_id,
            },
            "salary_rate": {
                "id":         self.salary_rate.id,
                "class_type": self.salary_rate.class_type,
                "amount":     self.salary_rate.amount,
            }
        }
        if include_attendances:
            data["attendances"] = [a.to_dict() for a in self.attendances]
        return data