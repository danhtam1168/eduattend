from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.admin import Admin
from app.models.teacher import Teacher


class AuthService:
    @staticmethod
    def login(username, password):
        """
        Xử lý đăng nhập cho cả Admin và Giáo viên.
        Trả về tuple: (token, user_dict)
        Raise ValueError nếu có lỗi.
        """
        # Tìm trong admins trước
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if not admin.check_password(password):
                raise ValueError("Tên đăng nhập hoặc mật khẩu không đúng")
            if not admin.is_active:
                raise ValueError("Tài khoản đã bị khoá")
            token = create_access_token(identity=f"admin:{admin.id}")
            return token, admin.to_dict()

        # Tìm trong teachers
        teacher = Teacher.query.filter_by(username=username).first()
        if teacher:
            if not teacher.check_password(password):
                raise ValueError("Tên đăng nhập hoặc mật khẩu không đúng")
            if teacher.status == 'pending':
                raise ValueError("Tài khoản đang chờ admin phê duyệt")
            if teacher.status == 'rejected':
                raise ValueError("Tài khoản đã bị từ chối")
            if teacher.status in ('inactive', 'on_leave') or not teacher.is_active:
                raise ValueError("Tài khoản đã bị khoá hoặc tạm nghỉ")
            token = create_access_token(identity=f"teacher:{teacher.id}")
            return token, teacher.to_dict()

        raise ValueError("Tên đăng nhập hoặc mật khẩu không đúng")

    @staticmethod
    def register_teacher(data):
        """
        Giáo viên tự đăng ký. Trả về teacher model.
        """
        username = data['username'].strip()
        
        if Teacher.query.filter_by(username=username).first() or \
           Admin.query.filter_by(username=username).first():
            raise ValueError("Username đã được sử dụng")

        if len(data['password']) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")

        teacher = Teacher(
            username=username,
            full_name=data['full_name'].strip(),
            specialization=data.get('specialization', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            status='pending'
        )
        teacher.set_password(data['password'])
        db.session.add(teacher)
        db.session.commit()
        return teacher

    @staticmethod
    def change_password(role, uid, old_password, new_password):
        if role == 'admin':
            user = Admin.query.get(uid)
        else:
            user = Teacher.query.get(uid)

        if not user or not user.check_password(old_password):
            raise ValueError("Mật khẩu cũ không đúng")

        if len(new_password) < 6:
            raise ValueError("Mật khẩu mới phải có ít nhất 6 ký tự")

        user.set_password(new_password)
        db.session.commit()
