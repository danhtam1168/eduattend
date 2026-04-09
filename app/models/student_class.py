from datetime import datetime, date
from app.extensions import db


class StudentClass(db.Model):
    __tablename__ = 'student_classes'

    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id        = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=date.today)
    fee_amount      = db.Column(db.Numeric(10, 2), nullable=False)   # Học phí gốc / buổi
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    final_fee       = db.Column(db.Numeric(10, 2), nullable=False)   # Học phí sau giảm
    status          = db.Column(
        db.Enum('active', 'completed', 'dropped', name='student_class_status'),
        default='active', nullable=False
    )
    notes           = db.Column(db.Text, nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique: 1 học sinh chỉ đăng ký 1 lần 1 lớp
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', name='uq_student_class'),
    )

    # Relationships
    student = db.relationship('Student', backref='enrollments')
    class_  = db.relationship('Class', backref='enrollments')

    def to_dict(self, include_student=True):
        data = {
            "id":               self.id,
            "student_id":       self.student_id,
            "class_id":         self.class_id,
            "enrollment_date":  self.enrollment_date.isoformat() if self.enrollment_date else None,
            "fee_amount":       float(self.fee_amount),
            "discount_percent": float(self.discount_percent),
            "discount_amount":  float(self.discount_amount),
            "final_fee":        float(self.final_fee),
            "status":           self.status,
            "notes":            self.notes,
        }
        if include_student and self.student:
            data["student"] = {
                "id":           self.student.id,
                "student_code": self.student.student_code,
                "full_name":    self.student.full_name,
                "phone":        self.student.phone,
                "parent_phone": self.student.parent_phone,
            }
        return data
