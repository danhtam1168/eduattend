from flask import Blueprint, request
from app.services.subject_service import SubjectService
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

subjects_bp = Blueprint('admin_subjects', __name__)

@subjects_bp.route('', methods=['GET'])
@admin_required
def get_subjects():
    try:
        subjects = SubjectService.get_subjects()
        return success_response([s.to_dict() for s in subjects])
    except Exception as e:
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@subjects_bp.route('', methods=['POST'])
@admin_required
def create_subject():
    data = request.get_json()
    errors = validate_required(data, ['subject_name', 'fee_per_session'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    from app.extensions import db
    try:
        subject = SubjectService.create_subject(data)
        return success_response(subject.to_dict(), "Tạo môn học thành công", 201)
    except ValueError as e:
        if "tồn tại" in str(e).lower():
            return error_response(str(e), 409)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@subjects_bp.route('/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    data = request.get_json()
    from app.extensions import db
    try:
        subject = SubjectService.update_subject(subject_id, data)
        return success_response(subject.to_dict(), "Cập nhật thành công")
    except ValueError as e:
        if "không tồn tại" in str(e).lower():
            return error_response(str(e), 404)
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)

@subjects_bp.route('/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    from app.extensions import db
    try:
        SubjectService.delete_subject(subject_id)
        return success_response(message="Đã ẩn môn học")
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Lỗi hệ thống: {str(e)}", 500)
