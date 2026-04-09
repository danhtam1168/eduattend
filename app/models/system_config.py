from datetime import datetime
from app.extensions import db


class SystemConfig(db.Model):
    __tablename__ = 'system_configs'

    id           = db.Column(db.Integer, primary_key=True)
    config_key   = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text, nullable=True)
    description  = db.Column(db.Text, nullable=True)
    data_type    = db.Column(
        db.Enum('string', 'number', 'boolean', 'json', name='config_data_type'),
        default='string', nullable=False
    )
    is_active    = db.Column(db.Boolean, default=True, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id":           self.id,
            "config_key":   self.config_key,
            "config_value": self.config_value,
            "description":  self.description,
            "data_type":    self.data_type,
            "is_active":    self.is_active,
        }
