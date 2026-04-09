from datetime import date
from app.extensions import db
from app.models.teacher_attendance import TeacherAttendance
from app.models.student_attendance import StudentAttendance
from app.models.schedule import Schedule
from app.models.student_class import StudentClass

class AttendanceService:
    @staticmethod
    def get_teacher_attendances(teacher_id, class_id, from_date, to_date):
        query = TeacherAttendance.query
        if teacher_id:
            query = query.filter_by(teacher_id=int(teacher_id))
        if class_id:
            query = query.filter_by(class_id=int(class_id))
        if from_date:
            query = query.filter(TeacherAttendance.attendance_date >= date.fromisoformat(from_date))
        if to_date:
            query = query.filter(TeacherAttendance.attendance_date <= date.fromisoformat(to_date))

        return query.order_by(TeacherAttendance.attendance_date.desc()).all()

    @staticmethod
    def create_teacher_attendance(data, admin_id):
        existing = TeacherAttendance.query.filter_by(
            teacher_id=int(data['teacher_id']),
            class_id=int(data['class_id']),
            attendance_date=data['attendance_date']
        ).first()
        if existing:
            raise ValueError("Đã có bản ghi chấm công cho giáo viên này trong ngày")

        sched = Schedule.query.filter_by(
            class_id=int(data['class_id']),
            schedule_date=data['attendance_date']
        ).first()

        record = TeacherAttendance(
            teacher_id=int(data['teacher_id']),
            class_id=int(data['class_id']),
            schedule_id=sched.id if sched else None,
            attendance_date=date.fromisoformat(data['attendance_date']),
            session_count=float(data.get('session_count', 1)),
            status=data.get('status', 'present'),
            notes=data.get('notes', ''),
            recorded_by=admin_id,
        )
        db.session.add(record)

        if record.status == 'absent':
            enrollments = StudentClass.query.filter_by(class_id=record.class_id, status='active').all()
            for enr in enrollments:
                if not StudentAttendance.query.filter_by(
                    student_id=enr.student_id, class_id=record.class_id,
                    attendance_date=record.attendance_date
                ).first():
                    sa = StudentAttendance(
                        student_id=enr.student_id,
                        class_id=record.class_id,
                        teacher_attendance_id=record.id,
                        attendance_date=record.attendance_date,
                        status='teacher_cancelled',
                        teacher_id=record.teacher_id,
                    )
                    db.session.add(sa)

        db.session.commit()
        return record

    @staticmethod
    def update_teacher_attendance(record_id, data):
        record = TeacherAttendance.query.get(record_id)
        if not record:
            raise ValueError("Bản ghi không tồn tại")

        editable = ['status', 'session_count', 'notes']
        for field in editable:
            if field in data:
                setattr(record, field, data[field])

        db.session.commit()
        return record

    @staticmethod
    def get_session_students(schedule_id, teacher_id):
        sched = Schedule.query.get(schedule_id)
        if not sched:
            raise ValueError("Lịch học không tồn tại")
        if sched.teacher_id != teacher_id:
            raise ValueError("Đây không phải lịch dạy của bạn")

        teacher_att = TeacherAttendance.query.filter_by(
            teacher_id=teacher_id, class_id=sched.class_id, attendance_date=sched.schedule_date
        ).first()
        if not teacher_att:
            raise ValueError("Vui lòng chấm công trước khi điểm danh học sinh")

        enrollments = StudentClass.query.filter_by(class_id=sched.class_id, status='active').all()

        att_map = {}
        for att in StudentAttendance.query.filter_by(
            class_id=sched.class_id, attendance_date=sched.schedule_date
        ).all():
            att_map[att.student_id] = att

        students = []
        for enr in enrollments:
            s = enr.student
            att = att_map.get(s.id)
            students.append({
                **s.to_dict(),
                "attendance_status": att.status if att else None,
                "attendance_note":   att.notes if att else None,
                "attendance_id":     att.id if att else None,
            })

        return {
            "schedule": sched.to_dict(),
            "teacher_attendance": teacher_att.to_dict(include_relations=False),
            "students": students,
        }

    @staticmethod
    def mark_student_attendance(schedule_id, teacher_id, attendances):
        sched = Schedule.query.get(schedule_id)
        if not sched:
            raise ValueError("Lịch học không tồn tại")
        if sched.teacher_id != teacher_id:
            raise ValueError("Đây không phải lịch dạy của bạn")

        teacher_att = TeacherAttendance.query.filter_by(
            teacher_id=teacher_id, class_id=sched.class_id, attendance_date=sched.schedule_date
        ).first()
        if not teacher_att:
            raise ValueError("Vui lòng chấm công trước khi điểm danh học sinh")

        if not attendances:
            raise ValueError("Danh sách điểm danh không được để trống")

        VALID_STATUSES = ('present', 'absent_excused', 'absent_unexcused', 'teacher_cancelled')
        present_count = 0
        for item in attendances:
            student_id = item.get('student_id')
            status = item.get('status', 'present')
            note = item.get('note', '')

            if not student_id:
                continue
            if status not in VALID_STATUSES:
                raise ValueError(f"Trạng thái không hợp lệ: {status}")

            existing = StudentAttendance.query.filter_by(
                student_id=int(student_id), class_id=sched.class_id, attendance_date=sched.schedule_date
            ).first()

            if existing:
                existing.status = status
                existing.notes = note
            else:
                existing = StudentAttendance(
                    student_id=int(student_id),
                    class_id=sched.class_id,
                    teacher_attendance_id=teacher_att.id,
                    attendance_date=sched.schedule_date,
                    status=status,
                    notes=note,
                    teacher_id=teacher_id,
                )
                db.session.add(existing)

            if status == 'present':
                present_count += 1

        db.session.commit()
        return len(attendances), present_count
