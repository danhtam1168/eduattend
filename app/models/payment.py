from datetime import datetime, date
from app.extensions import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    fee_id          = db.Column(db.Integer, db.ForeignKey('monthly_fees.id'), nullable=True)
    payment_date    = db.Column(db.Date, default=date.today)
    amount          = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method  = db.Column(
        db.Enum('cash', 'bank_transfer', 'online_payment', name='payment_method'),
        nullable=False
    )
    transaction_ref = db.Column(db.String(100), nullable=True)
    status          = db.Column(
        db.Enum('pending', 'completed', 'failed', 'refunded', name='payment_status'),
        default='completed', nullable=False
    )
    notes           = db.Column(db.Text, nullable=True)
    received_by     = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student    = db.relationship('Student', backref='payments')
    monthly_fee = db.relationship('MonthlyFee', backref='payments')
    receiver   = db.relationship('Admin', backref='received_payments')

    def to_dict(self):
        return {
            "id":              self.id,
            "student_id":      self.student_id,
            "fee_id":          self.fee_id,
            "payment_date":    self.payment_date.isoformat() if self.payment_date else None,
            "amount":          float(self.amount),
            "payment_method":  self.payment_method,
            "transaction_ref": self.transaction_ref,
            "status":          self.status,
            "notes":           self.notes,
            "student": {
                "id":        self.student.id,
                "full_name": self.student.full_name,
                "student_code": self.student.student_code,
            } if self.student else None,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
        }
