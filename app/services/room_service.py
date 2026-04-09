from app.extensions import db
from app.models.room import Room

class RoomService:
    @staticmethod
    def get_rooms(status=None):
        query = Room.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Room.room_name).all()

    @staticmethod
    def create_room(data):
        room_name = data['room_name'].strip()
        if Room.query.filter_by(room_name=room_name).first():
            raise ValueError("Tên phòng đã tồn tại")

        room = Room(
            room_name=room_name,
            room_number=data.get('room_number', ''),
            capacity=int(data['capacity']),
            equipment=data.get('equipment', ''),
            location=data.get('location', ''),
        )
        db.session.add(room)
        db.session.commit()
        return room

    @staticmethod
    def update_room(room_id, data):
        room = Room.query.get(room_id)
        if not room:
            raise ValueError("Phòng học không tồn tại")

        editable = ['room_name', 'room_number', 'capacity', 'equipment', 'location', 'status']
        for field in editable:
            if field in data:
                setattr(room, field, data[field])

        db.session.commit()
        return room
