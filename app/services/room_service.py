from app.extensions import db
from app.models.room import Room

class RoomService:
    @staticmethod
    def get_rooms(status=None, check_day=None, check_start=None, check_end=None):
        query = Room.query
        if status:
            query = query.filter_by(status=status)
            
        if check_day is not None and check_start and check_end:
            from app.models.class_schedule import ClassSchedule
            # Lọc những phòng vướng lịch trong khung giờ đó (ClassSchedule có chung day_of_week và overlap giờ)
            occupied_rooms = db.session.query(ClassSchedule.room_id).filter(
                ClassSchedule.day_of_week == int(check_day),
                ClassSchedule.room_id.isnot(None),
                ClassSchedule.start_time < check_end, 
                ClassSchedule.end_time > check_start
            ).distinct().all()
            
            occupied_ids = [r[0] for r in occupied_rooms]
            if occupied_ids:
                query = query.filter(Room.id.notin_(occupied_ids))

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

    @staticmethod
    def delete_room(room_id):
        room = Room.query.get(room_id)
        if not room:
            raise ValueError("Phòng học không tồn tại")
        
        from sqlalchemy.exc import IntegrityError
        try:
            db.session.delete(room)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Không thể xoá phòng học này vì đã có dữ liệu xếp lịch hoặc bị ràng buộc bởi hệ thống.")

    @staticmethod
    def delete_room(room_id):
        room = Room.query.get(room_id)
        if not room:
            raise ValueError("Phòng học không tồn tại")
        
        from sqlalchemy.exc import IntegrityError
        try:
            db.session.delete(room)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Không thể xoá phòng học này vì đã có dữ liệu xếp lịch hoặc lớp học ràng buộc.")
