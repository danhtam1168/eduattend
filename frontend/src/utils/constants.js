export const SHIFTS = {
  morning:   'Sáng',
  afternoon: 'Chiều',
  evening:   'Tối',
};

export const SESSION_STATUS = {
  pending:   { label: 'Chờ xác nhận', color: 'pending' },
  confirmed: { label: 'Đã xác nhận',  color: 'confirmed' },
  cancelled: { label: 'Đã huỷ',       color: 'cancelled' },
};

export const USER_ROLES = {
  admin:   'Admin',
  teacher: 'Giáo viên',
};

export const ATTENDANCE_STATUS = {
  true:  { label: 'Có mặt',  color: 'present' },
  false: { label: 'Vắng mặt', color: 'absent' },
  null:  { label: 'Chưa điểm danh', color: 'pending' },
};
