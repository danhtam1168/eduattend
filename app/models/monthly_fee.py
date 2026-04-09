from datetime import datetime
from app.extensions import db


class MonthlyFee(db.Model):
    """
    Học phí hàng tháng.
    Công thức: billable_sessions = attended_sessions + excused_absences
    Không tính phí: unexcused_absences + teacher_cancelled
    """
    __tablename__ = 'monthly_fees'

    id                  = db.Column(db.Integer, primary_key=True)
    student_id          = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id            = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    month_year          = db.Column(db.String(7), nullable=False)   # "2025-04"
    total_sessions      = db.Column(db.Integer, nullable=False)
    attended_sessions   = db.Column(db.Integer, default=0)
    excused_absences    = db.Column(db.Integer, default=0)
    unexcused_absences  = db.Column(db.Integer, default=0)
    teacher_cancelled   = db.Column(db.Integer, default=0)
    billable_sessions   = db.Column(db.Integer, nullable=False)     # Số buổi tính tiền
    fee_per_session     = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount        = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount     = db.Column(db.Numeric(10, 2), default=0)
    final_amount        = db.Column(db.Numeric(10, 2), nullable=False)
    status              = db.Column(
        db.Enum('draft', 'confirmed', 'paid', 'overdue', name='monthly_fee_status'),
        default='draft', nullable=False
    )
    due_date            = db.Column(db.Date, nullable=True)
    notes               = db.Column(db.Text, nullable=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique: 1 học sinh / 1 lớp / 1 tháng
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', 'month_year', name='uq_fee_student_class_month'),
    )

    # Relationships
    student = db.relationship('Student', backref='monthly_fees')
    class_  = db.relationship('Class', backref='monthly_fees')

    def to_dict(self):
        return {
            "id":                 self.id,
            "student_id":         self.student_id,
            "class_id":           self.class_id,
            "month_year":         self.month_year,
            "total_sessions":     self.total_sessions,
            "attended_sessions":  self.attended_sessions,
            "excused_absences":   self.excused_absences,
            "unexcused_absences": self.unexcused_absences,
            "teacher_cancelled":  self.teacher_cancelled,
            "billable_sessions":  self.billable_sessions,
            "fee_per_session":    float(self.fee_per_session),
            "total_amount":       float(self.total_amount),
            "discount_amount":    float(self.discount_amount),
            "final_amount":       float(self.final_amount),
            "status":             self.status,
            "due_date":           self.due_date.isoformat() if self.due_date else None,
            "notes":              self.notes,
            "student": {
                "id":           self.student.id,
                "full_name":    self.student.full_name,
                "student_code": self.student.student_code,
            } if self.student else None,
            "class_": {
                "id":         self.class_.id,
                "class_name": self.class_.class_name,
            } if self.class_ else None,
            "created_at":         self.created_at.isoformat() if self.created_at else None,
        }
