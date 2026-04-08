# EduAttend — Frontend Coding Guidelines

> **Stack:** React 18 + Vite 5 + CSS Modules  
> **Backend:** Flask REST API (port 5000)  
> **Design:** Figma "Attendance Management System" — Golden Yellow theme

---

## 1. Cấu trúc thư mục

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/              # Hình ảnh, icons tĩnh
│   │   └── logo.svg
│   ├── components/          # UI components tái sử dụng
│   │   ├── ui/              # Atomic: Button, Input, Badge, Table, Modal, Card
│   │   ├── layout/          # Sidebar, Header, Layout, ProtectedRoute
│   │   └── shared/          # StatusBadge, AvatarCard, StatCard, EmptyState
│   ├── pages/               # Trang (route-level)
│   │   ├── Login/
│   │   │   ├── Login.jsx
│   │   │   └── Login.module.css
│   │   ├── admin/
│   │   │   ├── Dashboard/
│   │   │   ├── Teachers/
│   │   │   ├── Students/
│   │   │   ├── Sessions/
│   │   │   ├── SalaryReport/
│   │   │   └── Settings/
│   │   └── teacher/
│   │       ├── MySessions/
│   │       ├── SessionDetail/
│   │       └── MarkAttendance/
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useTeachers.js
│   │   ├── useStudents.js
│   │   └── useSessions.js
│   ├── services/            # API calls
│   │   ├── api.js           # Axios instance + interceptors
│   │   ├── authService.js
│   │   ├── adminService.js
│   │   └── teacherService.js
│   ├── store/               # Zustand global state
│   │   ├── authStore.js
│   │   └── uiStore.js
│   ├── utils/               # Helpers
│   │   ├── formatters.js    # format ngày, tiền, giờ
│   │   └── constants.js     # SHIFT_LABELS, STATUS_COLORS, etc.
│   ├── styles/
│   │   ├── variables.css    # Design tokens (màu, font, spacing)
│   │   └── global.css       # Reset + base styles
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── .env                     # VITE_API_URL=http://localhost:5000
├── .env.example
├── vite.config.js
└── package.json
```

---

## 2. Design Tokens (từ Figma)

```css
/* src/styles/variables.css */
:root {
  /* === COLORS === */
  /* Primary — Golden Yellow (màu chủ đạo Figma) */
  --color-primary:        #F2B43A;
  --color-primary-dark:   #D49A20;
  --color-primary-light:  #FDE9B3;
  --color-primary-bg:     #FFF8EC;

  /* Status */
  --color-present:        #22C55E;  /* Xanh lá — Present */
  --color-present-bg:     #DCFCE7;
  --color-absent:         #EF4444;  /* Đỏ — Absent */
  --color-absent-bg:      #FEE2E2;
  --color-late:           #F59E0B;  /* Vàng — Late */
  --color-late-bg:        #FEF3C7;
  --color-pending:        #6B7280; /* Xám — Pending */
  --color-pending-bg:     #F3F4F6;
  --color-confirmed:      #3B82F6; /* Xanh dương — Confirmed */
  --color-confirmed-bg:   #DBEAFE;

  /* Neutrals */
  --color-bg:             #F8F9FA;
  --color-surface:        #FFFFFF;
  --color-border:         #E5E7EB;
  --color-border-strong:  #D1D5DB;

  /* Text */
  --color-text:           #111827;
  --color-text-secondary: #6B7280;
  --color-text-muted:     #9CA3AF;

  /* Sidebar */
  --sidebar-bg:           #1C1C2E;   /* Dark navy */
  --sidebar-text:         #A0A0B0;
  --sidebar-active-bg:    #F2B43A;
  --sidebar-active-text:  #1C1C2E;
  --sidebar-width:        240px;
  --sidebar-icon-color:   #A0A0B0;

  /* === TYPOGRAPHY === */
  --font-family:          'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs:         0.75rem;   /* 12px */
  --font-size-sm:         0.875rem;  /* 14px */
  --font-size-base:       1rem;      /* 16px */
  --font-size-lg:         1.125rem;  /* 18px */
  --font-size-xl:         1.25rem;   /* 20px */
  --font-size-2xl:        1.5rem;    /* 24px */
  --font-size-3xl:        1.875rem;  /* 30px */

  /* === SPACING === */
  --space-1:  0.25rem;
  --space-2:  0.5rem;
  --space-3:  0.75rem;
  --space-4:  1rem;
  --space-5:  1.25rem;
  --space-6:  1.5rem;
  --space-8:  2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;

  /* === RADIUS === */
  --radius-sm:  4px;
  --radius-md:  8px;
  --radius-lg:  12px;
  --radius-xl:  16px;
  --radius-full: 9999px;

  /* === SHADOWS === */
  --shadow-sm:  0 1px 3px rgba(0,0,0,.08);
  --shadow-md:  0 4px 12px rgba(0,0,0,.10);
  --shadow-lg:  0 8px 24px rgba(0,0,0,.12);

  /* === TRANSITIONS === */
  --transition-fast:   150ms ease;
  --transition-base:   250ms ease;
  --transition-slow:   400ms ease;
}
```

---

## 3. Naming Conventions

### Files & Folders
| Loại | Convention | Ví dụ |
|------|-----------|-------|
| Component | PascalCase | `StatusBadge.jsx` |
| CSS Module | `ComponentName.module.css` | `StatusBadge.module.css` |
| Hook | camelCase, tiền tố `use` | `useTeachers.js` |
| Service | camelCase, hậu tố `Service` | `adminService.js` |
| Store | camelCase, hậu tố `Store` | `authStore.js` |
| Util | camelCase | `formatters.js` |
| Page folder | PascalCase | `Teachers/` |

### Component Naming
```jsx
// ✅ Đúng
const StatusBadge = ({ status }) => { ... }
export default StatusBadge;

// ❌ Sai
const status_badge = ...
export default function() { ... }
```

---

## 4. Component Patterns

### 4.1 UI Atomic Components
```jsx
// src/components/ui/Button.jsx
const Button = ({
  children,
  variant = 'primary',  // 'primary' | 'secondary' | 'ghost' | 'danger'
  size = 'md',          // 'sm' | 'md' | 'lg'
  loading = false,
  disabled = false,
  onClick,
  type = 'button',
  className = '',
}) => { ... }
```

### 4.2 Page Component Structure
```jsx
// pages/admin/Teachers/Teachers.jsx
import styles from './Teachers.module.css';

const Teachers = () => {
  // 1. State & hooks
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);

  // 2. Data fetching
  useEffect(() => { fetchTeachers(); }, []);

  // 3. Event handlers
  const handleCreate = async (data) => { ... };

  // 4. Render
  return (
    <div className={styles.container}>
      {/* JSX */}
    </div>
  );
};

export default Teachers;
```

---

## 5. API Service Pattern

```js
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — tự động đính kèm JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle 401 auto logout
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;
```

---

## 6. State Management (Zustand)

```js
// src/store/authStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(persist(
  (set) => ({
    user: null,
    token: null,
    isAuthenticated: false,

    login: (user, token) => set({ user, token, isAuthenticated: true }),
    logout: () => {
      localStorage.removeItem('access_token');
      set({ user: null, token: null, isAuthenticated: false });
    },
    setUser: (user) => set({ user }),
  }),
  { name: 'auth-storage' }
));

export default useAuthStore;
```

---

## 7. CSS Modules Rules

```css
/* ✅ Đúng — dùng camelCase cho class names */
.container { ... }
.headerTitle { ... }
.statusBadge { ... }

/* ❌ Sai — không dùng BEM hay kebab-case */
.header-title { ... }
.status__badge--active { ... }
```

```jsx
// ✅ Đúng
import styles from './Teachers.module.css';
<div className={styles.container}>
<div className={`${styles.card} ${styles.active}`}>

// Dùng clsx nếu có nhiều điều kiện
import clsx from 'clsx';
<div className={clsx(styles.badge, {
  [styles.present]: status === 'present',
  [styles.absent]: status === 'absent',
})}>
```

---

## 8. Constants

```js
// src/utils/constants.js
export const SHIFTS = {
  morning:   'Sáng',
  afternoon: 'Chiều',
  evening:   'Tối',
};

export const SESSION_STATUS = {
  pending:   { label: 'Chờ xác nhận', color: 'pending' },
  confirmed: { label: 'Đã xác nhận',  color: 'confirmed' },
  cancelled: { label: 'Đã huỷ',       color: 'absent' },
};

export const USER_ROLES = {
  admin:   'Admin',
  teacher: 'Giáo viên',
};
```

---

## 9. Formatters

```js
// src/utils/formatters.js
export const formatDate = (dateStr) => {
  if (!dateStr) return '---';
  return new Date(dateStr).toLocaleDateString('vi-VN');
};

export const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return '---';
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency', currency: 'VND'
  }).format(amount);
};

export const formatShift = (shift) => SHIFTS[shift] || shift;
```

---

## 10. Do's & Don'ts

### ✅ DO
- Dùng CSS Modules cho tất cả component styles
- Dùng design tokens (CSS variables) — không hardcode màu sắc
- Tách API calls vào `services/`, không gọi axios trực tiếp trong component
- Xử lý loading và error states trong mọi data-fetch
- Đặt text tiếng Việt cho UI (labels, messages, placeholders)
- Dùng `<Link>` của React Router, không dùng `<a href>`

### ❌ DON'T
- Không hardcode URL API trong component — luôn dùng service
- Không đặt inline styles (trừ dynamic values như width %)
- Không lưu sensitive data vào localStorage (chỉ token là OK)
- Không gọi API trong render function — dùng `useEffect`
- Không quên xử lý error khi gọi API

---

## 11. Routing Structure

```
/login                    → Login (public)
/                         → redirect theo role
  /admin/
    /dashboard            → Dashboard (Admin)
    /teachers             → Danh sách giáo viên
    /teachers/:id         → Chi tiết giáo viên
    /students             → Danh sách học sinh
    /sessions             → Tất cả buổi dạy (Logs)
    /salary-report        → Báo cáo lương
    /settings             → Cài đặt (Salary rates)
  /teacher/
    /sessions             → Buổi dạy của tôi
    /sessions/:id         → Chi tiết buổi dạy
    /sessions/:id/attend  → Điểm danh học sinh
    /profile              → Thông tin cá nhân
```

---

## 12. Figma → Component Mapping

| Figma Screen | React Page | Route |
|-------------|------------|-------|
| Login | `Login.jsx` | `/login` |
| Admin Dashboard | `Dashboard.jsx` | `/admin/dashboard` |
| Employee List | `Teachers.jsx` | `/admin/teachers` |
| Employee Details | `TeacherDetail.jsx` | `/admin/teachers/:id` |
| Register | `CreateTeacher.jsx` | `/admin/teachers/new` |
| Logs | `Sessions.jsx` | `/admin/sessions` |
| Report | `SalaryReport.jsx` | `/admin/salary-report` |
| Settings | `Settings.jsx` | `/admin/settings` |
| (Teacher) My Sessions | `MySessions.jsx` | `/teacher/sessions` |
| (Teacher) Mark Attendance | `MarkAttendance.jsx` | `/teacher/sessions/:id/attend` |
