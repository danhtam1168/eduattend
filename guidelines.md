# 📘 CODING GUIDELINES — Hệ thống chấm công Flask REST API

> Tài liệu này định nghĩa toàn bộ nguyên tắc code, flow, và chuẩn API cho project.
> Mọi thành viên (hoặc chính bạn sau 3 tháng) đọc file này là hiểu được toàn bộ hệ thống.

---

## 1. NGUYÊN TẮC CHUNG (General Principles)

### 1.1 Triết lý code
- **Rõ ràng hơn thông minh** — code dễ đọc quan trọng hơn code ngắn
- **Một hàm, một việc** — mỗi function chỉ làm đúng 1 nhiệm vụ
- **Fail fast** — validate input sớm nhất có thể, trả lỗi ngay nếu sai
- **Không magic number** — dùng constant hoặc Enum thay cho số/chuỗi cứng

### 1.2 Đặt tên
```
# Variables & functions: snake_case
teacher_id, get_session_by_id(), confirm_teaching_session()

# Classes: PascalCase
TeachingSession, SalaryRate, StudentAttendance

# Constants: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_PAGE_SIZE = 20

# Routes: kebab-case (URL)
/api/v1/teaching-sessions
/api/v1/salary-rates

# Database columns: snake_case
employee_id, confirmed_at, is_active
```

### 1.3 Cấu trúc file
- Mỗi file không quá **300 dòng** — nếu vượt, tách module
- Import theo thứ tự: stdlib → third-party → local
- Mỗi model một file riêng trong `app/models/`
- Mỗi nhóm API một file riêng trong `app/api/`

---

## 2. KIẾN TRÚC MVC + SERVICE LAYER

### 2.1 Sơ đồ tổng quan
```
Browser/Client
     │
     ▼
[Templates / Frontend]  ← Jinja2 hoặc gọi API trực tiếp
     │
     ▼
[Routes / Controllers]  ← app/api/*.py  — chỉ nhận request, gọi service, trả response
     │
     ▼
[Services]              ← app/services/*.py — chứa toàn bộ business logic
     │
     ▼
[Models / ORM]          ← app/models/*.py — định nghĩa bảng, quan hệ
     │
     ▼
[Database - PostgreSQL]
```

### 2.2 Trách nhiệm từng tầng

#### Route/Controller (`app/api/`)
```python
# ✅ Đúng — Controller chỉ làm 3 việc:
# 1. Lấy data từ request
# 2. Gọi service
# 3. Trả response

@teacher_bp.route('/sessions/<int:session_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_session(session_id):
    teacher_id = get_jwt_identity()
    result, error = SessionService.confirm_session(session_id, teacher_id)
    if error:
        return error_response(error, 400)
    return success_response(result, "Xác nhận buổi dạy thành công")


# ❌ Sai — Controller không được chứa business logic
@teacher_bp.route('/sessions/<int:session_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_session(session_id):
    session = TeachingSession.query.get(session_id)
    if session.status == 'confirmed':       # ← logic này phải nằm ở Service
        return jsonify({"error": "..."}), 400
    session.status = 'confirmed'            # ← và cả đây
    db.session.commit()
    return jsonify({"success": True})
```

#### Service (`app/services/`)
```python
# ✅ Service chứa toàn bộ logic nghiệp vụ
class SessionService:
    @staticmethod
    def confirm_session(session_id: int, teacher_id: int):
        """
        Xác nhận một buổi dạy.
        Returns: (data, error) — nếu thành công error=None, ngược lại data=None
        """
        session = TeachingSession.query.get(session_id)

        if not session:
            return None, "Buổi dạy không tồn tại"

        if session.teacher_id != teacher_id:
            return None, "Bạn không có quyền xác nhận buổi dạy này"

        if session.status == 'confirmed':
            return None, "Buổi dạy đã được xác nhận trước đó"

        if session.status == 'cancelled':
            return None, "Buổi dạy đã bị huỷ, không thể xác nhận"

        session.status = 'confirmed'
        session.confirmed_at = datetime.utcnow()
        db.session.commit()

        return session.to_dict(), None
```

#### Model (`app/models/`)
```python
# Model chỉ định nghĩa:
# - Cấu trúc bảng
# - Quan hệ (relationship)
# - to_dict() để serialize
# KHÔNG chứa business logic

class TeachingSession(db.Model):
    __tablename__ = 'teaching_sessions'

    id             = db.Column(db.Integer, primary_key=True)
    teacher_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salary_rate_id = db.Column(db.Integer, db.ForeignKey('salary_rates.id'), nullable=False)
    date           = db.Column(db.Date, nullable=False)
    shift          = db.Column(db.Enum('morning', 'afternoon', 'evening', name='shift_enum'), nullable=False)
    status         = db.Column(db.Enum('pending', 'confirmed', 'cancelled', name='session_status'), default='pending')
    confirmed_at   = db.Column(db.DateTime, nullable=True)
    note           = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    teacher        = db.relationship('User', backref='sessions')
    salary_rate    = db.relationship('SalaryRate', backref='sessions')
    attendances    = db.relationship('StudentAttendance', backref='session', lazy='dynamic')

    def to_dict(self):
        return {
            "id":           self.id,
            "date":         self.date.isoformat(),
            "shift":        self.shift,
            "status":       self.status,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "note":         self.note,
            "teacher": {
                "id":       self.teacher.id,
                "name":     self.teacher.full_name,
            },
            "salary_rate": {
                "id":         self.salary_rate.id,
                "class_type": self.salary_rate.class_type,
                "amount":     self.salary_rate.amount,
            }
        }
```

---

## 3. CHUẨN RESPONSE API

### 3.1 Wrapper chuẩn — dùng cho toàn bộ project
```python
# app/utils/response.py

from flask import jsonify

def success_response(data=None, message="Thành công", status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status_code

def error_response(message="Có lỗi xảy ra", status_code=400, errors=None):
    body = {
        "success": False,
        "message": message,
        "data": None
    }
    if errors:
        body["errors"] = errors  # Chi tiết lỗi validation
    return jsonify(body), status_code

def paginated_response(items, total, page, per_page):
    return success_response({
        "items": items,
        "pagination": {
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page
        }
    })
```

### 3.2 HTTP Status Code chuẩn
```
200 OK           — GET thành công, PUT/PATCH thành công
201 Created      — POST tạo mới thành công
400 Bad Request  — Input sai, thiếu field, sai format
401 Unauthorized — Chưa đăng nhập / token hết hạn
403 Forbidden    — Đã đăng nhập nhưng không có quyền
404 Not Found    — Resource không tồn tại
409 Conflict     — Trùng lặp (VD: đã xác nhận rồi)
500 Server Error — Lỗi server không mong muốn
```

### 3.3 Ví dụ response thực tế
```json
// ✅ Thành công — GET /api/v1/teacher/sessions?month=2025-01
{
  "success": true,
  "message": "Thành công",
  "data": {
    "items": [
      {
        "id": 12,
        "date": "2025-01-15",
        "shift": "morning",
        "status": "confirmed",
        "confirmed_at": "2025-01-15T08:30:00",
        "salary_rate": { "class_type": "Lớp nâng cao", "amount": 200000 }
      }
    ],
    "pagination": { "total": 20, "page": 1, "per_page": 10, "pages": 2 }
  }
}

// ❌ Lỗi validation — POST /api/v1/auth/login thiếu field
{
  "success": false,
  "message": "Dữ liệu không hợp lệ",
  "data": null,
  "errors": {
    "employee_id": "Mã nhân viên không được để trống",
    "password":    "Mật khẩu phải có ít nhất 6 ký tự"
  }
}

// ❌ Lỗi quyền — 403
{
  "success": false,
  "message": "Bạn không có quyền thực hiện thao tác này",
  "data": null
}
```

---

## 4. NGUYÊN TẮC VALIDATE INPUT

### 4.1 Nguyên tắc chung
- **Validate trước, xử lý sau** — không bao giờ query DB khi input chưa được validate
- **Trả đủ lỗi một lần** — validate tất cả fields, trả hết lỗi cùng lúc (không trả từng lỗi một)
- **Làm sạch input** — strip() string, ép kiểu đúng trước khi dùng
- **Không tin tưởng client** — dù frontend đã validate, backend phải validate lại

### 4.2 Validator helper
```python
# app/utils/validators.py

def validate_required(data: dict, fields: list) -> dict:
    """Kiểm tra các field bắt buộc, trả về dict lỗi"""
    errors = {}
    for field in fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f"'{field}' không được để trống"
    return errors

def validate_date_format(date_str: str) -> bool:
    """Kiểm tra format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_month_format(month_str: str) -> bool:
    """Kiểm tra format YYYY-MM"""
    try:
        datetime.strptime(month_str, '%Y-%m')
        return True
    except ValueError:
        return False
```

### 4.3 Ví dụ validate trong Service
```python
class SessionService:
    @staticmethod
    def create_session(data: dict):
        # Bước 1: Validate required fields
        errors = validate_required(data, ['teacher_id', 'date', 'shift', 'salary_rate_id'])

        # Bước 2: Validate từng field cụ thể
        if 'date' in data and not validate_date_format(data.get('date', '')):
            errors['date'] = "Ngày không đúng định dạng YYYY-MM-DD"

        if 'shift' in data and data['shift'] not in ['morning', 'afternoon', 'evening']:
            errors['shift'] = "Ca dạy phải là: morning, afternoon, evening"

        if errors:
            return None, errors  # Trả lỗi sớm

        # Bước 3: Validate logic nghiệp vụ
        teacher = User.query.get(data['teacher_id'])
        if not teacher or teacher.role != 'teacher':
            return None, {"teacher_id": "Giáo viên không tồn tại"}

        # Kiểm tra trùng lịch
        existing = TeachingSession.query.filter_by(
            teacher_id=data['teacher_id'],
            date=data['date'],
            shift=data['shift']
        ).first()
        if existing:
            return None, {"session": "Giáo viên đã có lịch dạy ca này"}

        # Bước 4: Tạo mới
        session = TeachingSession(**data)
        db.session.add(session)
        db.session.commit()
        return session.to_dict(), None
```

---

## 5. FLOW FRONTEND → API

### 5.1 Flow đăng nhập
```
[Form Login]
     │  POST /api/v1/auth/login
     │  Body: { employee_id, password }
     ▼
[API] Validate input
     │
     ▼
[API] Kiểm tra employee_id tồn tại
     │
     ▼
[API] Kiểm tra password (bcrypt.check)
     │
     ▼
[API] Tạo JWT token (access_token)
     │
     ▼
[Frontend] Lưu token vào localStorage/cookie
     │
     ▼
[Frontend] Redirect → /dashboard (theo role)
```

### 5.2 Flow giáo viên xác nhận buổi dạy
```
[Trang Teacher Dashboard]
     │  GET /api/v1/teacher/sessions?date=today
     │  Header: Authorization: Bearer <token>
     ▼
[Hiển thị danh sách buổi dạy hôm nay]
     │
     │  [Bấm "Xác nhận có dạy"]
     │  POST /api/v1/teacher/sessions/{id}/confirm
     ▼
[API] Xác thực JWT → lấy teacher_id
     │
     ▼
[API] Kiểm tra session tồn tại & thuộc teacher này
     │
     ▼
[API] Kiểm tra status còn pending không
     │
     ▼
[API] Cập nhật status=confirmed, confirmed_at=now
     │
     ▼
[Frontend] Cập nhật UI — đổi nút thành "Đã xác nhận ✓"
```

### 5.3 Flow điểm danh học sinh
```
[Trang điểm danh — sau khi confirm buổi]
     │  GET /api/v1/teacher/sessions/{id}/students
     ▼
[Hiển thị danh sách học sinh của buổi đó]
     │
     │  [Check từng học sinh có mặt/vắng]
     │  POST /api/v1/teacher/sessions/{id}/attendance
     │  Body: { attendances: [{ student_id, is_present }] }
     ▼
[API] Validate: session phải status=confirmed
     │
     ▼
[API] Upsert từng StudentAttendance record
     │
     ▼
[Frontend] Hiển thị tổng: "8/10 học sinh có mặt"
```

### 5.4 Flow admin xem báo cáo lương
```
[Trang Admin - Báo cáo]
     │  GET /api/v1/admin/salary/report?month=2025-01
     ▼
[API] Validate format tháng
     │
     ▼
[API] Query: JOIN sessions + salary_rates
      GROUP BY teacher
      WHERE status='confirmed' AND month=?
     │
     ▼
[API] Tính total_sessions, total_salary mỗi giáo viên
     │
     ▼
[Frontend] Hiển thị bảng lương
     │
     │  [Bấm "Xuất Excel"]
     │  GET /api/v1/admin/salary/export?month=2025-01
     ▼
[API] Dùng openpyxl tạo file Excel
[API] Trả về file với Content-Type: application/vnd.ms-excel
```

---

## 6. AUTHENTICATION & AUTHORIZATION

### 6.1 Nguyên tắc JWT
```python
# Mỗi request cần auth phải có header:
# Authorization: Bearer <access_token>

# Phân quyền bằng decorator
from functools import wraps
from flask_jwt_extended import get_jwt_identity

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return error_response("Chỉ admin mới có quyền truy cập", 403)
        return fn(*args, **kwargs)
    return wrapper

def teacher_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return error_response("Tài khoản không tồn tại hoặc đã bị khoá", 401)
        return fn(*args, **kwargs)
    return wrapper
```

### 6.2 Sử dụng decorator
```python
# Route chỉ admin
@admin_bp.route('/teachers', methods=['GET'])
@admin_required
def get_teachers(): ...

# Route chỉ teacher
@teacher_bp.route('/sessions', methods=['GET'])
@teacher_required
def get_my_sessions(): ...

# Route không cần auth
@auth_bp.route('/login', methods=['POST'])
def login(): ...
```

---

## 7. NGUYÊN TẮC DATABASE

### 7.1 Luôn dùng Migration
```bash
# Tạo migration sau khi thay đổi model
flask db migrate -m "add confirmed_at to teaching_sessions"
flask db upgrade

# KHÔNG bao giờ sửa trực tiếp DB trên production
```

### 7.2 Soft delete — không xoá cứng
```python
# ✅ Dùng is_active = False thay vì DELETE
user.is_active = False
db.session.commit()

# Khi query luôn filter is_active
User.query.filter_by(is_active=True).all()
```

### 7.3 Tránh N+1 query
```python
# ❌ N+1 — mỗi session lại query thêm teacher
sessions = TeachingSession.query.all()
for s in sessions:
    print(s.teacher.full_name)  # Query thêm N lần

# ✅ Dùng joinedload
from sqlalchemy.orm import joinedload
sessions = TeachingSession.query.options(
    joinedload(TeachingSession.teacher),
    joinedload(TeachingSession.salary_rate)
).all()
```

---

## 8. BIẾN MÔI TRƯỜNG & CONFIG

### 8.1 Không bao giờ hardcode secret
```python
# ❌ Sai
SECRET_KEY = "my-super-secret-key"
DATABASE_URL = "postgresql://user:pass@localhost/db"

# ✅ Đúng
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
```

### 8.2 File .env.example (commit lên git)
```env
# .env.example — template, không có giá trị thật
FLASK_ENV=development
SECRET_KEY=change-me-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/attendance_db
JWT_SECRET_KEY=change-me-in-production
JWT_ACCESS_TOKEN_EXPIRES=86400
```

### 8.3 .gitignore bắt buộc
```
.env
__pycache__/
*.pyc
instance/
.pytest_cache/
venv/
```

---

## 9. GIT WORKFLOW

### 9.1 Commit message convention
```
feat: thêm API xác nhận buổi dạy
fix: sửa lỗi validate ngày không đúng format
docs: cập nhật README hướng dẫn deploy
refactor: tách SessionService ra file riêng
chore: thêm requirements.txt
```

### 9.2 Branch strategy (đơn giản cho solo)
```
main          — production, chỉ merge khi ổn định
develop       — branch phát triển chính
feature/xxx   — tính năng mới (VD: feature/attendance-api)
fix/xxx       — sửa bug
```

---

## 10. CHECKLIST TRƯỚC KHI PUSH / DEPLOY

```
Code:
[ ] Không có print() debug còn sót
[ ] Không có secret/password hardcode
[ ] Tất cả API đều có validate input
[ ] Tất cả API đều dùng success_response / error_response chuẩn
[ ] Không có logic trong Controller (chỉ ở Service)

Database:
[ ] Đã tạo migration file mới nếu thay đổi model
[ ] Đã test migration upgrade / downgrade

Git:
[ ] .env không bị commit
[ ] requirements.txt đã cập nhật (pip freeze > requirements.txt)
[ ] Commit message rõ ràng

Deploy (Render):
[ ] Procfile có: web: gunicorn run:app
[ ] Biến môi trường đã set trên Render dashboard
[ ] DATABASE_URL đã fix postgres:// → postgresql://
```

---

*Cập nhật lần cuối: khi bắt đầu project — version 1.0*