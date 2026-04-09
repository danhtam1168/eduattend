from datetime import datetime, date
from app.extensions import db, bcrypt


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id              = db.Column(db.Integer, primary_key=True)
    teacher_code    = db.Column(db.String(6), unique=True, nullable=True)   # GV001 — sinh sau khi approve
    full_name       = db.Column(db.String(100), nullable=False)
    username        = db.Column(db.String(50), unique=True, nullable=False)
    password_hash   = db.Column(db.String(255), nullable=False)
    specialization  = db.Column(db.String(100), nullable=True)
    hire_date       = db.Column(db.Date, default=date.today, nullable=True)
    rate_per_session = db.Column(db.Numeric(10, 2), nullable=True)          # Có thể set sau
    bank_account    = db.Column(db.String(50), nullable=True)
    phone           = db.Column(db.String(15), nullable=True)
    address         = db.Column(db.Text, nullable=True)
    status          = db.Column(
        db.Enum('pending', 'active', 'inactive', 'on_leave', 'rejected', name='teacher_status'),
        default='pending', nullable=False
    )
    notes           = db.Column(db.Text, nullable=True)
    submitted_by    = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    approved_by     = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    approved_at     = db.Column(db.DateTime, nullable=True)
    is_active       = db.Column(db.Boolean, default=True, nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    approver        = db.relationship('Admin', foreign_keys=[approved_by], backref='approved_teachers')

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        data = {
            "id":              self.id,
            "teacher_code":    self.teacher_code,
            "full_name":       self.full_name,
            "username":        self.username,
            "specialization":  self.specialization,
            "hire_date":       self.hire_date.isoformat() if self.hire_date else None,
            "rate_per_session": float(self.rate_per_session) if self.rate_per_session else None,
            "phone":           self.phone,
            "address":         self.address,
            "status":          self.status,
            "role":            "teacher",  # dùng để frontend nhận biết loại
            "is_active":       self.is_active,
            "approved_at":     self.approved_at.isoformat() if self.approved_at else None,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
        }
        if include_sensitive:
            data["bank_account"] = self.bank_account
            data["notes"] = self.notes
        return data
