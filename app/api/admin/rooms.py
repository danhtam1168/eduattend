from flask import Blueprint, request
from app.extensions import db
from app.models.room import Room
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

rooms_bp = Blueprint('admin_rooms', __name__)


@rooms_bp.route('', methods=['GET'])
@admin_required
def get_rooms():
    status = request.args.get('status')
    query = Room.query
    if status:
        query = query.filter_by(status=status)
    rooms = query.order_by(Room.room_name).all()
    return success_response([r.to_dict() for r in rooms])


@rooms_bp.route('', methods=['POST'])
@admin_required
def create_room():
    data = request.get_json()
    errors = validate_required(data, ['room_name', 'capacity'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if Room.query.filter_by(room_name=data['room_name'].strip()).first():
        return error_response("Tên phòng đã tồn tại", 409)

    room = Room(
        room_name=data['room_name'].strip(),
        room_number=data.get('room_number', ''),
        capacity=int(data['capacity']),
        equipment=data.get('equipment', ''),
        location=data.get('location', ''),
    )
    db.session.add(room)
    db.session.commit()
    return success_response(room.to_dict(), "Thêm phòng học thành công", 201)


@rooms_bp.route('/<int:room_id>', methods=['PUT'])
@admin_required
def update_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        return error_response("Phòng học không tồn tại", 404)

    data = request.get_json()
    editable = ['room_name', 'room_number', 'capacity', 'equipment', 'location', 'status']
    for field in editable:
        if field in data:
            setattr(room, field, data[field])

    db.session.commit()
    return success_response(room.to_dict(), "Cập nhật thành công")
