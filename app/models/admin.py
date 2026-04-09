from datetime import datetime
from app.extensions import db, bcrypt


class Admin(db.Model):
    __tablename__ = 'admins'

    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email       = db.Column(db.String(100), unique=True, nullable=True)
    phone       = db.Column(db.String(15), nullable=True)
    full_name   = db.Column(db.String(100), nullable=True)
    role_type   = db.Column(
        db.Enum('admin', 'manager', 'staff', name='admin_role_type'),
        nullable=False, default='admin'
    )
    is_active   = db.Column(db.Boolean, default=True, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id":        self.id,
            "username":  self.username,
            "email":     self.email,
            "phone":     self.phone,
            "full_name": self.full_name,
            "role_type": self.role_type,
            "role":      "admin",          # dùng để frontend nhận biết loại tài khoản
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
