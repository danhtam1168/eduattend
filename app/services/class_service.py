from datetime import date
from app.extensions import db
from app.models.class_ import Class
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.student_class import StudentClass

class ClassService:
    @staticmethod
    def get_classes(status, teacher_id, subject_id, page, per_page):
        query = Class.query
        if status:
            query = query.filter_by(status=status)
        if teacher_id:
            query = query.filter_by(teacher_id=int(teacher_id))
        if subject_id:
            query = query.filter_by(subject_id=int(subject_id))

        total = query.count()
        classes = query.order_by(Class.start_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return classes.items, total

    @staticmethod
    def create_class(data):
        if not Subject.query.get(data['subject_id']):
            raise ValueError("Môn học không tồn tại")

        teacher = Teacher.query.get(data['teacher_id'])
        if not teacher or teacher.status != 'active':
            raise ValueError("Giáo viên không tồn tại hoặc chưa được kích hoạt")

        if data.get('class_code') and Class.query.filter_by(class_code=data['class_code']).first():
            raise ValueError("Mã lớp đã tồn tại")

        cls = Class(
            class_name=data['class_name'].strip(),
            class_code=data.get('class_code', '').strip() or None,
            subject_id=int(data['subject_id']),
            teacher_id=int(data['teacher_id']),
            room_id=data.get('room_id'),
            max_students=data.get('max_students', 15),
            start_date=date.fromisoformat(data['start_date']),
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            schedule_days=data.get('schedule_days', ''),
            schedule_time=data.get('schedule_time'),
            duration_minutes=data.get('duration_minutes', 90),
            notes=data.get('notes', ''),
        )
        db.session.add(cls)
        db.session.commit()
        return cls

    @staticmethod
    def get_class(class_id):
        cls = Class.query.get(class_id)
        if not cls:
            raise ValueError("Lớp học không tồn tại")
        return cls

    @staticmethod
    def update_class(class_id, data):
        cls = Class.query.get(class_id)
        if not cls:
            raise ValueError("Lớp học không tồn tại")

        editable = ['class_name', 'class_code', 'teacher_id', 'room_id',
                    'max_students', 'end_date', 'schedule_days', 'schedule_time',
                    'duration_minutes', 'status', 'notes']
        for field in editable:
            if field in data:
                setattr(cls, field, data[field])

        db.session.commit()
        return cls

    @staticmethod
    def get_class_students(class_id):
        cls = Class.query.get(class_id)
        if not cls:
            raise ValueError("Lớp học không tồn tại")

        enrollments = StudentClass.query.filter_by(class_id=class_id, status='active').all()
        return enrollments

    @staticmethod
    def enroll_student(class_id, data):
        cls = Class.query.get(class_id)
        if not cls:
            raise ValueError("Lớp học không tồn tại")
        if cls.status != 'active':
            raise ValueError("Lớp học không còn hoạt động")
        if cls.current_students >= cls.max_students:
            raise ValueError("Lớp học đã đầy")

        student = Student.query.get(int(data['student_id']))
        if not student or not student.is_active:
            raise ValueError("Học sinh không tồn tại")

        if StudentClass.query.filter_by(class_id=class_id, student_id=student.id, status='active').first():
            raise ValueError("Học sinh đã đăng ký lớp này")

        fee = float(data.get('fee_amount', cls.subject.fee_per_session))
        discount_percent = float(data.get('discount_percent', 0))
        discount_amount = fee * discount_percent / 100
        final_fee = fee - discount_amount

        enrollment = StudentClass(
            student_id=student.id,
            class_id=class_id,
            fee_amount=fee,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            final_fee=final_fee,
            notes=data.get('notes', '')
        )
        cls.current_students = (cls.current_students or 0) + 1
        db.session.add(enrollment)
        db.session.commit()
        return enrollment

    @staticmethod
    def remove_student(class_id, student_id):
        enrollment = StudentClass.query.filter_by(class_id=class_id, student_id=student_id, status='active').first()
        if not enrollment:
            raise ValueError("Học sinh chưa đăng ký lớp này")

        enrollment.status = 'dropped'
        cls = Class.query.get(class_id)
        if cls and cls.current_students > 0:
            cls.current_students -= 1
        db.session.commit()
