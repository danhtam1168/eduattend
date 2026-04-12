from app.extensions import db
from app.models.student import Student

class StudentService:
    @staticmethod
    def _generate_student_code():
        last = Student.query.filter(
            Student.student_code.isnot(None)
        ).order_by(Student.student_code.desc()).first()
        if last and last.student_code:
            try:
                num = int(last.student_code[2:]) + 1
            except ValueError:
                num = 1
        else:
            num = 1
        return f"HS{num:03d}"

    @staticmethod
    def get_students(status, search, page, per_page):
        query = Student.query
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(Student.full_name.ilike(f'%{search}%'))

        total = query.count()
        students = query.order_by(Student.full_name).paginate(page=page, per_page=per_page, error_out=False)
        return students.items, total

    @staticmethod
    def create_student(data):
        referred_by = data.get('referred_by')
        if referred_by:
            # Check if referrer exists
            referrer = Student.query.get(referred_by)
            if not referrer:
                raise ValueError("Người giới thiệu không tồn tại")
        else:
            referred_by = None

        student = Student(
            student_code=StudentService._generate_student_code(),
            full_name=data['full_name'].strip(),
            date_of_birth=data.get('date_of_birth'),
            referred_by=referred_by,
            address=data.get('address', ''),
            parent_phone=data.get('parent_phone', ''),
            phone=data.get('phone', ''),
            notes=data.get('notes', ''),
            status='active'
        )
        db.session.add(student)
        db.session.commit()
        return student

    @staticmethod
    def get_student(student_id):
        student = Student.query.get(student_id)
        if not student:
            raise ValueError("Học sinh không tồn tại")
        return student

    @staticmethod
    def update_student(student_id, data):
        student = Student.query.get(student_id)
        if not student:
            raise ValueError("Học sinh không tồn tại")

        editable = ['full_name', 'date_of_birth', 'referred_by', 'address',
                    'parent_phone', 'phone', 'status', 'notes', 'is_active']
        for field in editable:
            if field in data:
                val = data[field]
                if field == 'referred_by':
                    if not val:
                        val = None
                    else:
                        if int(val) == student_id:
                            raise ValueError("Học sinh không thể tự giới thiệu chính mình")
                        referrer = Student.query.get(val)
                        if not referrer:
                            raise ValueError("Người giới thiệu không tồn tại")
                
                setattr(student, field, val)

        db.session.commit()
        return student

    @staticmethod
    def deactivate_student(student_id):
        student = Student.query.get(student_id)
        if not student:
            raise ValueError("Học sinh không tồn tại")
        student.is_active = False
        student.status = 'inactive'
        db.session.commit()
