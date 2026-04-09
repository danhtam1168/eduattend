from datetime import datetime
from app.extensions import db


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id          = db.Column(db.Integer, primary_key=True)
    admin_id    = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    action      = db.Column(db.String(100), nullable=False)
    table_name  = db.Column(db.String(50), nullable=True)
    record_id   = db.Column(db.Integer, nullable=True)
    old_values  = db.Column(db.Text, nullable=True)
    new_values  = db.Column(db.Text, nullable=True)
    ip_address  = db.Column(db.String(45), nullable=True)
    user_agent  = db.Column(db.Text, nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship('Admin', backref='activity_logs')

    def to_dict(self):
        return {
            "id":         self.id,
            "admin_id":   self.admin_id,
            "action":     self.action,
            "table_name": self.table_name,
            "record_id":  self.record_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
