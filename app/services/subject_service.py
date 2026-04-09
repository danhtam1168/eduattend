from app.extensions import db
from app.models.subject import Subject

class SubjectService:
    @staticmethod
    def get_subjects():
        return Subject.query.filter_by(is_active=True).order_by(Subject.subject_name).all()

    @staticmethod
    def create_subject(data):
        subject_code = data.get('subject_code', '').strip() or None
        if subject_code and Subject.query.filter_by(subject_code=subject_code).first():
            raise ValueError("Mã môn học đã tồn tại")

        subject = Subject(
            subject_name=data['subject_name'].strip(),
            subject_code=subject_code,
            description=data.get('description', ''),
            grade_level=data.get('grade_level', ''),
            fee_per_session=data['fee_per_session'],
            duration_minutes=data.get('duration_minutes', 90),
        )
        db.session.add(subject)
        db.session.commit()
        return subject

    @staticmethod
    def update_subject(subject_id, data):
        subject = Subject.query.get(subject_id)
        if not subject:
            raise ValueError("Môn học không tồn tại")

        editable = ['subject_name', 'subject_code', 'description', 'grade_level',
                    'fee_per_session', 'duration_minutes', 'is_active']
        for field in editable:
            if field in data:
                setattr(subject, field, data[field])

        db.session.commit()
        return subject

    @staticmethod
    def delete_subject(subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            raise ValueError("Môn học không tồn tại")
        subject.is_active = False
        db.session.commit()
