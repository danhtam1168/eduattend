from datetime import datetime, date
from app.extensions import db


class TeacherSalary(db.Model):
    """Bảng lương giáo viên hàng tháng — tính dựa trên teacher_attendances"""
    __tablename__ = 'teacher_salaries'

    id               = db.Column(db.Integer, primary_key=True)
    teacher_id       = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    month_year       = db.Column(db.String(7), nullable=False)      # "2025-04"
    total_sessions   = db.Column(db.Numeric(6, 2), nullable=False)  # Tổng số buổi
    rate_per_session = db.Column(db.Numeric(10, 2), nullable=False)
    base_salary      = db.Column(db.Numeric(12, 2), nullable=False)
    bonus            = db.Column(db.Numeric(10, 2), default=0)
    deduction        = db.Column(db.Numeric(10, 2), default=0)
    advance_payment  = db.Column(db.Numeric(10, 2), default=0)
    net_salary       = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date     = db.Column(db.Date, nullable=True)
    status           = db.Column(
        db.Enum('draft', 'approved', 'paid', name='salary_status'),
        default='draft', nullable=False
    )
    notes            = db.Column(db.Text, nullable=True)
    approved_by      = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    paid_by          = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique: 1 giáo viên / 1 tháng
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'month_year', name='uq_salary_teacher_month'),
    )

    # Relationships
    teacher  = db.relationship('Teacher', backref='salaries')
    approver = db.relationship('Admin', foreign_keys=[approved_by], backref='approved_salaries')
    payer    = db.relationship('Admin', foreign_keys=[paid_by], backref='paid_salaries')

    def to_dict(self):
        return {
            "id":               self.id,
            "teacher_id":       self.teacher_id,
            "month_year":       self.month_year,
            "total_sessions":   float(self.total_sessions),
            "rate_per_session": float(self.rate_per_session),
            "base_salary":      float(self.base_salary),
            "bonus":            float(self.bonus),
            "deduction":        float(self.deduction),
            "advance_payment":  float(self.advance_payment),
            "net_salary":       float(self.net_salary),
            "payment_date":     self.payment_date.isoformat() if self.payment_date else None,
            "status":           self.status,
            "notes":            self.notes,
            "teacher": {
                "id":           self.teacher.id,
                "teacher_code": self.teacher.teacher_code,
                "full_name":    self.teacher.full_name,
            } if self.teacher else None,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
        }
