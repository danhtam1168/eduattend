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
        query = Student.query.filter_by(is_active=True)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(Student.full_name.ilike(f'%{search}%'))

        total = query.count()
        students = query.order_by(Student.full_name).paginate(page=page, per_page=per_page, error_out=False)
        return students.items, total

    @staticmethod
    def create_student(data):
        student = Student(
            student_code=StudentService._generate_student_code(),
            full_name=data['full_name'].strip(),
            date_of_birth=data.get('date_of_birth'),
            referred_by=data.get('referred_by'),
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
                setattr(student, field, data[field])

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
