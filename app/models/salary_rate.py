from datetime import datetime
from app.extensions import db


class SalaryRate(db.Model):
    __tablename__ = 'salary_rates'

    id          = db.Column(db.Integer, primary_key=True)
    class_type  = db.Column(db.String(100), nullable=False)
    amount      = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active   = db.Column(db.Boolean, default=True, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id":          self.id,
            "class_type":  self.class_type,
            "amount":      self.amount,
            "description": self.description,
            "is_active":   self.is_active,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }