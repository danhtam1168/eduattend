from datetime import datetime
from app.extensions import db
from app.models.teacher import Teacher
from app.models.admin import Admin

class TeacherService:
    @staticmethod
    def _generate_teacher_code():
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

    @staticmethod
    def get_teachers(status, page, per_page):
        query = Teacher.query
        if status:
            query = query.filter_by(status=status)
        else:
            query = query.filter(Teacher.status != 'rejected')
        query = query.order_by(Teacher.created_at.desc())
        total = query.count()
        teachers = query.paginate(page=page, per_page=per_page, error_out=False)
        return teachers.items, total

    @staticmethod
    def create_teacher(data, admin_id):
        if Teacher.query.filter_by(username=data['username'].strip()).first():
            raise ValueError("Username đã được sử dụng")

        teacher_code = TeacherService._generate_teacher_code()
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
            approved_by=admin_id,
            approved_at=datetime.utcnow(),
        )
        teacher.set_password(data['password'])
        db.session.add(teacher)
        db.session.commit()
        return teacher

    @staticmethod
    def approve_teacher(teacher_id, admin_id, data):
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            raise ValueError("Giáo viên không tồn tại")
        if teacher.status != 'pending':
            raise ValueError(f"Tài khoản không ở trạng thái pending (hiện tại: {teacher.status})")

        teacher.teacher_code = TeacherService._generate_teacher_code()
        teacher.status = 'active'
        teacher.approved_by = admin_id
        teacher.approved_at = datetime.utcnow()

        if data:
            if 'rate_per_session' in data and data['rate_per_session']:
                teacher.rate_per_session = data['rate_per_session']
            if 'hire_date' in data:
                from datetime import date
                teacher.hire_date = date.fromisoformat(data['hire_date'])

        db.session.commit()
        return teacher

    @staticmethod
    def reject_teacher(teacher_id, data):
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            raise ValueError("Giáo viên không tồn tại")
        if teacher.status != 'pending':
            raise ValueError("Chỉ có thể từ chối tài khoản đang pending")

        teacher.status = 'rejected'
        teacher.notes = data.get('reason', 'Bị từ chối bởi admin') if data else 'Bị từ chối bởi admin'
        db.session.commit()

    @staticmethod
    def update_teacher(teacher_id, data):
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            raise ValueError("Giáo viên không tồn tại")

        editable = ['full_name', 'specialization', 'phone', 'bank_account',
                    'rate_per_session', 'address', 'notes', 'status', 'is_active']
        for field in editable:
            if field in data:
                setattr(teacher, field, data[field])

        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")
            teacher.set_password(data['password'])

        db.session.commit()
        return teacher

    @staticmethod
    def deactivate_teacher(teacher_id):
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            raise ValueError("Giáo viên không tồn tại")
        teacher.status = 'inactive'
        teacher.is_active = False
        db.session.commit()

    @staticmethod
    def get_teacher(teacher_id):
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            raise ValueError("Giáo viên không tồn tại")
        return teacher

    @staticmethod
    def update_profile(teacher, data):
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != teacher.username:
                if Teacher.query.filter_by(username=new_username).first() or \
                   Admin.query.filter_by(username=new_username).first():
                    raise ValueError("Username đã được sử dụng")
                teacher.username = new_username

        safe_fields = ['phone', 'address', 'bank_account', 'specialization']
        for field in safe_fields:
            if field in data:
                setattr(teacher, field, data[field])

        db.session.commit()
        return teacher
