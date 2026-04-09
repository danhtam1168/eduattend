from datetime import datetime
from app.extensions import db


class Room(db.Model):
    __tablename__ = 'rooms'

    id          = db.Column(db.Integer, primary_key=True)
    room_name   = db.Column(db.String(50), unique=True, nullable=False)
    room_number = db.Column(db.String(20), nullable=True)
    capacity    = db.Column(db.Integer, nullable=False)
    equipment   = db.Column(db.Text, nullable=True)
    location    = db.Column(db.String(100), nullable=True)
    status      = db.Column(
        db.Enum('available', 'maintenance', 'occupied', name='room_status'),
        default='available', nullable=False
    )
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id":          self.id,
            "room_name":   self.room_name,
            "room_number": self.room_number,
            "capacity":    self.capacity,
            "equipment":   self.equipment,
            "location":    self.location,
            "status":      self.status,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }
