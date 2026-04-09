from datetime import datetime
from flask import Blueprint, request
from app.extensions import db
from app.models.teacher import Teacher
from app.utils.response import success_response, error_response, paginated_response
from app.utils.decorators import admin_required, get_current_admin
from app.utils.validators import validate_required

teachers_bp = Blueprint('admin_teachers', __name__)


def _generate_teacher_code():
    """Tự động sinh mã GV001, GV002..."""
    last = Teacher.query.filter(
        Teacher.teacher_code.isnot(None)
    ).order_by(Teacher.teacher_code.desc()).first()

    if last and last.teacher_code:
        try:
            num = int(last.teacher_code[2:]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    return f"GV{num:03d}"


# ─── DANH SÁCH GIÁO VIÊN ─────────────────────────────────────────────────────

@teachers_bp.route('', methods=['GET'])
@admin_required
def get_teachers():
    status = request.args.get('status')       # pending|active|inactive|rejected
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    query = Teacher.query
    if status:
        query = query.filter_by(status=status)
    else:
        # Mặc định trả về tất cả trừ rejected
        query = query.filter(Teacher.status != 'rejected')

    query = query.order_by(Teacher.created_at.desc())
    total = query.count()
    teachers = query.paginate(page=page, per_page=per_page, error_out=False)

    return paginated_response(
        items=[t.to_dict(include_sensitive=True) for t in teachers.items],
        total=total, page=page, per_page=per_page
    )


# ─── TẠO GIÁO VIÊN (Admin tạo thay) ─────────────────────────────────────────

@teachers_bp.route('', methods=['POST'])
@admin_required
def create_teacher():
    data = request.get_json()
    errors = validate_required(data, ['username', 'password', 'full_name'])
    if errors:
        return error_response("Dữ liệu không hợp lệ", 400, errors)

    if Teacher.query.filter_by(username=data['username'].strip()).first():
        return error_response("Username đã được sử dụng", 409)

    teacher_code = _generate_teacher_code()
    teacher = Teacher(
        teacher_code=teacher_code,
        full_name=data['full_name'].strip(),
        username=data['username'].strip(),
        specialization=data.get('specialization', ''),
        phone=data.get('phone', ''),
        bank_account=data.get('bank_account', ''),
        rate_per_session=data.get('rate_per_session'),
        address=data.get('address', ''),
        notes=data.get('notes', ''),
        status='active',
        approved_by=get_current_admin().id,
        approved_at=datetime.utcnow(),
    )
    teacher.set_password(data['password'])
    db.session.add(teacher)
    db.session.commit()

    return success_response(teacher.to_dict(include_sensitive=True), "Tạo giáo viên thành công", 201)


# ─── APPROVE GIÁO VIÊN ───────────────────────────────────────────────────────

@teachers_bp.route('/<int:teacher_id>/approve', methods=['PUT'])
@admin_required
def approve_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return error_response("Giáo viên không tồn tại", 404)
    if teacher.status != 'pending':
        return error_response(f"Tài khoản không ở trạng thái pending (hiện tại: {teacher.status})", 400)

    admin = get_current_admin()
    data = request.get_json() or {}

    teacher.teacher_code = _generate_teacher_code()
    teacher.status = 'active'
    teacher.approved_by = admin.id
    teacher.approved_at = datetime.utcnow()

    # Admin có thể set rate khi approve
    if 'rate_per_session' in data and data['rate_per_session']:
        teacher.rate_per_session = data['rate_per_session']
    if 'hire_date' in data:
        from datetime import date
        teacher.hire_date = date.fromisoformat(data['hire_date'])

    db.session.commit()
    return success_response(teacher.to_dict(include_sensitive=True), f"Đã phê duyệt giáo viên. Mã GV: {teacher.teacher_code}")


# ─── REJECT GIÁO VIÊN ────────────────────────────────────────────────────────

@teachers_bp.route('/<int:teacher_id>/reject', methods=['PUT'])
@admin_required
def reject_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return error_response("Giáo viên không tồn tại", 404)
    if teacher.status != 'pending':
        return error_response("Chỉ có thể từ chối tài khoản đang pending", 400)

    data = request.get_json() or {}
    teacher.status = 'rejected'
    teacher.notes = data.get('reason', 'Bị từ chối bởi admin')
    db.session.commit()
    return success_response(message="Đã từ chối tài khoản giáo viên")


# ─── CẬP NHẬT GIÁO VIÊN ──────────────────────────────────────────────────────

@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return error_response("Giáo viên không tồn tại", 404)

    data = request.get_json()
    editable = ['full_name', 'specialization', 'phone', 'bank_account',
                'rate_per_session', 'address', 'notes', 'status', 'is_active']
    for field in editable:
        if field in data:
            setattr(teacher, field, data[field])

    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return error_response("Mật khẩu phải có ít nhất 6 ký tự", 400)
        teacher.set_password(data['password'])

    db.session.commit()
    return success_response(teacher.to_dict(include_sensitive=True), "Cập nhật thành công")


# ─── XOÁ MỀM GIÁO VIÊN ───────────────────────────────────────────────────────

@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
@admin_required
def deactivate_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return error_response("Giáo viên không tồn tại", 404)
    teacher.status = 'inactive'
    teacher.is_active = False
    db.session.commit()
    return success_response(message="Đã khoá tài khoản giáo viên")


# ─── CHI TIẾT GIÁO VIÊN ──────────────────────────────────────────────────────

@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
@admin_required
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return error_response("Giáo viên không tồn tại", 404)
    return success_response(teacher.to_dict(include_sensitive=True))
