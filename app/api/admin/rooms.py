from flask import Blueprint, request
from app.services.room_service import RoomService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

rooms_bp = Blueprint('admin_rooms', __name__)

@rooms_bp.route('', methods=['GET'])
@admin_required
def get_rooms():
    try:
        status = request.args.get('status')
        rooms = RoomService.get_rooms(status)
        return success_response([r.to_dict() for r in rooms])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@rooms_bp.route('', methods=['POST'])
@admin_required
def create_room():
    data = request.get_json()
    errors = validate_required(data, ['room_name', 'capacity'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        room = RoomService.create_room(data)
        return success_response(room.to_dict(), "Thêm phòng học thành công", 201)
    except ValueError as e:
        if "tồn tại" in str(e).lower():
            return error_response(str(e), 409)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@rooms_bp.route('/<int:room_id>', methods=['PUT'])
@admin_required
def update_room(room_id):
    data = request.get_json()
    from app.extensions import db
    try:
        room = RoomService.update_room(room_id, data)
        return success_response(room.to_dict(), "Cập nhật thành công")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
