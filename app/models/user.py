from datetime import datetime
from app.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id          = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name   = db.Column(db.String(100), nullable=False)
    phone       = db.Column(db.String(15), nullable=True)
    email       = db.Column(db.String(120), nullable=True)
    role        = db.Column(db.Enum('admin', 'teacher', name='user_role'), default='teacher', nullable=False)
    is_active   = db.Column(db.Boolean, default=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id":          self.id,
            "employee_id": self.employee_id,
            "full_name":   self.full_name,
            "phone":       self.phone,
            "email":       self.email,
            "role":        self.role,
            "is_active":   self.is_active,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }