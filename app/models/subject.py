from datetime import datetime
from app.extensions import db


class Subject(db.Model):
    __tablename__ = 'subjects'

    id               = db.Column(db.Integer, primary_key=True)
    subject_name     = db.Column(db.String(100), nullable=False)
    subject_code     = db.Column(db.String(20), unique=True, nullable=True)
    description      = db.Column(db.Text, nullable=True)
    grade_level      = db.Column(db.String(20), nullable=True)
    fee_per_session  = db.Column(db.Numeric(10, 2), nullable=False)
    duration_minutes = db.Column(db.Integer, default=90, nullable=False)
    is_active        = db.Column(db.Boolean, default=True, nullable=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id":               self.id,
            "subject_name":     self.subject_name,
            "subject_code":     self.subject_code,
            "description":      self.description,
            "grade_level":      self.grade_level,
            "fee_per_session":  float(self.fee_per_session),
            "duration_minutes": self.duration_minutes,
            "is_active":        self.is_active,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
        }
