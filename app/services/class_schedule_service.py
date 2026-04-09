from app.extensions import db
from app.models.class_schedule import ClassSchedule
from app.models.class_ import Class
from app.models.schedule import Schedule
from datetime import datetime, date, timedelta, time

class ClassScheduleService:
    @staticmethod
    def get_templates(class_id=None):
        query = ClassSchedule.query
        if class_id:
            query = query.filter_by(class_id=class_id)
        return query.all()

    @staticmethod
    def create_template(data):
        cls = Class.query.get(data['class_id'])
        if not cls:
            raise ValueError("Lớp học không tồn tại")

        # Kiểm tra trùng lặp trong tuần của chính lớp này
        existing = ClassSchedule.query.filter_by(
            class_id=cls.id,
            day_of_week=data['day_of_week']
        ).first()

        if existing:
            # Update nếu đã có thứ này (Hoặc có thể lỗi nếu muốn nhiều slot 1 ngày)
            # Thường 1 lớp chỉ có 1 ca trong 1 ngày, nếu có ca khác thì update
            existing.start_time = time.fromisoformat(data['start_time'])
            existing.end_time = time.fromisoformat(data['end_time'])
            if 'room_id' in data:
                existing.room_id = data['room_id']
            tpl = existing
        else:
            tpl = ClassSchedule(
                class_id=cls.id,
                day_of_week=data['day_of_week'],
                start_time=time.fromisoformat(data['start_time']),
                end_time=time.fromisoformat(data['end_time']),
                room_id=data.get('room_id')
            )
            db.session.add(tpl)
        
        db.session.commit()
        
        # Sau khi tạo mẫu, ta có thể tự động generate các buổi dạy thực tế trong 30 ngày (hoặc theo end_date)
        ClassScheduleService.generate_real_schedules(cls.id)

        return tpl

    @staticmethod
    def delete_template(template_id):
        tpl = ClassSchedule.query.get(template_id)
        if not tpl:
            raise ValueError("Mẫu lịch không tồn tại")
        
        db.session.delete(tpl)
        db.session.commit()

    @staticmethod
    def generate_real_schedules(class_id):
        cls = Class.query.get(class_id)
        if not cls or not cls.start_date:
            return

        templates = ClassSchedule.query.filter_by(class_id=class_id).all()
        if not templates:
            return
            
        tmpl_dict = {t.day_of_week: t for t in templates}

        # Phóng lịch giới hạn từ start_date đến tối đa end_date hoặc 3 tháng (để tránh tạo quá nhiều)
        from_date = max(cls.start_date, date.today())
        to_date = cls.end_date if cls.end_date else (from_date + timedelta(days=90))
        
        # Ngăn tạo quá 6 tháng
        max_limit = from_date + timedelta(days=180)
        if to_date > max_limit:
            to_date = max_limit

        curr_date = from_date
        while curr_date <= to_date:
            # day_of_week trong datetime: Monday = 0, Sunday = 6
            # Cần khớp với quy ước frontend: Giả sử Frontend gửi 0=Thứ 2, 6=CN
            dow = curr_date.weekday()
            
            if dow in tmpl_dict:
                tpl = tmpl_dict[dow]
                # Kiểm tra xem ngày này đã có Schedule chưa
                existing_sched = Schedule.query.filter_by(
                    class_id=class_id,
                    schedule_date=curr_date
                ).first()
                
                if not existing_sched:
                    sched = Schedule(
                        class_id=class_id,
                        teacher_id=cls.teacher_id,
                        schedule_date=curr_date,
                        start_time=tpl.start_time,
                        end_time=tpl.end_time,
                        room_id=tpl.room_id or cls.room_id,
                        status='scheduled'
                    )
                    db.session.add(sched)
            
            curr_date += timedelta(days=1)
            
        db.session.commit()
