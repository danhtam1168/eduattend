from datetime import datetime, date
from app.extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    id              = db.Column(db.Integer, primary_key=True)
    student_code    = db.Column(db.String(10), unique=True, nullable=True)  # HS001 — sinh tự động
    full_name       = db.Column(db.String(100), nullable=False)
    date_of_birth   = db.Column(db.Date, nullable=True)
    referred_by     = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    address         = db.Column(db.Text, nullable=True)
    parent_phone    = db.Column(db.String(15), nullable=True)
    phone           = db.Column(db.String(15), nullable=True)
    enrollment_date = db.Column(db.Date, default=date.today, nullable=True)
    status          = db.Column(
        db.Enum('active', 'inactive', 'graduated', name='student_status'),
        default='active', nullable=False
    )
    notes           = db.Column(db.Text, nullable=True)
    is_active       = db.Column(db.Boolean, default=True, nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship (giới thiệu bởi HS khác)
    referred_student = db.relationship('Student', remote_side='Student.id', backref='referrals')

    def to_dict(self):
        return {
            "id":              self.id,
            "student_code":    self.student_code,
            "full_name":       self.full_name,
            "date_of_birth":   self.date_of_birth.isoformat() if self.date_of_birth else None,
            "referred_by":     self.referred_by,
            "address":         self.address,
            "parent_phone":    self.parent_phone,
            "phone":           self.phone,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "status":          self.status,
            "notes":           self.notes,
            "is_active":       self.is_active,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
        }