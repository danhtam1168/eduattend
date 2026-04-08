# Tech Stack - EduAttend System

## 1. Frontend (React)

- **Framework:** React 18.x (với Vite 5.x build tool tối ưu hiệu năng)
- **State Management:** Zustand (dùng cho authentication state và global UI state vì nhẹ và ít boilerplate)
- **Routing:** React Router v6 (Nested routes, Protected routes dựa trên role)
- **Styles:** Vanilla CSS + CSS Modules
  - **Design System:** Xây dựng toàn bộ dựa trên CSS Variables (`variables.css`), bám sát thiết kế Figma với màu chủ đạo **Golden Yellow (#F2B43A)** và dark navy theme chon sidebar.
  - Tự custom UI components (Button, Input, Modal, Table, Badge, Card) thay vì dùng framework thứ 3 để tối ưu kích thước cục bộ và giao diện chuẩn Figma 100%.
- **HTTP Client:** Axios (cấu hình interceptor tự gắn JWT token và bắt lỗi `401 Unauthorized` tự động logout)
- **Icons:** Lucide React (Bộ icon viền đẹp hiện đại, phù hợp UI layout)
- **Charts:** Recharts (Sẽ dùng trong tương lai cho Dashboard nếu mở rộng)

## 2. Backend (Flask API)

- **Framework:** Flask 3.x
- **CORS Support:** Flask-CORS (Bật API communication giữa React port `5173` và Flask port `5000`)
- **Database ORM:** SQLAlchemy 2.0 (tương tác với database SQLite/PostgreSQL)
- **Authentication:** Flask-JWT-Extended (Bảo mật bằng JWT Tokens, phân quyền `admin` / `teacher`)
- **Password Hasher:** Flask-Bcrypt (Hệ mã hoá mật khẩu an toàn)
- **Migrations:** Flask-Migrate (Alembic) để quản lý lịch sử schema của DB.

## 3. Kiến Trúc (Architecture)

**Decoupled RESTful Architecture:**
Frontend (Client) và Backend (API) sống độc lập hoàn toàn.
- Admin và Teacher dùng chung 1 app SPA (Single Page Application). Dựa vào dữ liệu từ `/api/auth/me`, Frontend tự động quyết định Sidebar Links và chuyển hướng (`Redirect`) màn hình tương ứng.
- **Tín hiệu Authentication:**
  1. Người dùng Login -> Nhận Access Token.
  2. Token lưu vào `localStorage` (quản lý bởi Zustand persist).
  3. Từ giờ, mọi request Axios đều kèm `Authorization: Bearer <token>`.
  4. Backend xác nhận logic `teacher_required` hoặc `admin_required`.

## 4. Tương lai (Roadmap mở rộng Face Recognition)
Với thiết kế Figma có màn hình **Upload** cho ảnh thẻ giáo viên:
- Ta có thể mở rộng tính năng upload Image base64 từ React lên Flask.
- Flask dùng thư viện Python `face_recognition` (dựa trên Dlib) để encode và nhận diện.
