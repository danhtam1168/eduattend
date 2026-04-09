from flask import Blueprint, request
from app.extensions import db
from app.models.subject import Subject
from app.utils.response import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_required

subjects_bp = Blueprint('admin_subjects', __name__)


@subjects_bp.route('', methods=['GET'])
@admin_required
def get_subjects():
    subjects = Subject.query.filter_by(is_active=True).order_by(Subject.subject_name).all()
    return success_response([s.to_dict() for s in subjects])


@subjects_bp.route('', methods=['POST'])
@admin_required
def create_subject():
    data = request.get_json()
    errors = validate_required(data, ['subject_name', 'fee_per_session'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if data.get('subject_code') and Subject.query.filter_by(subject_code=data['subject_code']).first():
        return error_response("Mã môn học đã tồn tại", 409)

    subject = Subject(
        subject_name=data['subject_name'].strip(),
        subject_code=data.get('subject_code', '').strip() or None,
        description=data.get('description', ''),
        grade_level=data.get('grade_level', ''),
        fee_per_session=data['fee_per_session'],
        duration_minutes=data.get('duration_minutes', 90),
    )
    db.session.add(subject)
    db.session.commit()
    return success_response(subject.to_dict(), "Tạo môn học thành công", 201)


@subjects_bp.route('/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return error_response("Môn học không tồn tại", 404)

    data = request.get_json()
    editable = ['subject_name', 'subject_code', 'description', 'grade_level',
                'fee_per_session', 'duration_minutes', 'is_active']
    for field in editable:
        if field in data:
            setattr(subject, field, data[field])

    db.session.commit()
    return success_response(subject.to_dict(), "Cập nhật thành công")


@subjects_bp.route('/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return error_response("Môn học không tồn tại", 404)
    subject.is_active = False
    db.session.commit()
    return success_response(message="Đã ẩn môn học")
