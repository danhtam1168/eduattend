import { useState, useEffect } from 'react';
import { UserPlus, Search, Edit2, Lock } from 'lucide-react';
import { Card, CardBody } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import styles from './Teachers.module.css';

const initForm = { employee_id: '', full_name: '', phone: '', email: '', password: '' };

const Teachers = () => {
  const [teachers, setTeachers] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [search,   setSearch]   = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editItem,  setEditItem]  = useState(null);
  const [form,      setForm]      = useState(initForm);
  const [saving,    setSaving]    = useState(false);
  const [error,     setError]     = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const res = await adminService.getTeachers();
      setTeachers(res.data || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(teachers.filter(t =>
      t.full_name.toLowerCase().includes(q) ||
      t.employee_id.toLowerCase().includes(q) ||
      (t.email || '').toLowerCase().includes(q)
    ));
  }, [search, teachers]);

  const openCreate = () => { setEditItem(null); setForm(initForm); setError(''); setModalOpen(true); };
  const openEdit   = (t)  => { setEditItem(t); setForm({ ...t, password: '' }); setError(''); setModalOpen(true); };
  const closeModal = ()   => { setModalOpen(false); setError(''); };

  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.employee_id || !form.full_name) {
      setError('Vui lòng nhập mã nhân viên và họ tên'); return;
    }
    if (!editItem && !form.password) {
      setError('Vui lòng nhập mật khẩu'); return;
    }
    setSaving(true);
    setError('');
    try {
      if (editItem) {
        const payload = { full_name: form.full_name, phone: form.phone, email: form.email };
        if (form.password) payload.password = form.password;
        await adminService.updateTeacher(editItem.id, payload);
      } else {
        await adminService.createTeacher(form);
      }
      closeModal();
      load();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi');
    } finally { setSaving(false); }
  };

  const handleDeactivate = async (t) => {
    if (!window.confirm(`Khoá tài khoản "${t.full_name}"?`)) return;
    await adminService.deactivateTeacher(t.id);
    load();
  };

  const columns = [
    {
      key: 'full_name', title: 'Giáo viên',
      render: (v, row) => {
        const initials = v?.split(' ').map(w => w[0]).slice(-2).join('').toUpperCase();
        return (
          <div className={styles.nameCell}>
            <div className={styles.avatar}>{initials}</div>
            <div>
              <div className={styles.teacherName}>{v}</div>
              <div className={styles.teacherId}>{row.employee_id}</div>
            </div>
          </div>
        );
      }
    },
    { key: 'phone',  title: 'Điện thoại' },
    { key: 'email',  title: 'Email' },
    {
      key: 'is_active', title: 'Trạng thái',
      render: (v) => <Badge color={v ? 'present' : 'absent'}>{v ? 'Hoạt động' : 'Khoá'}</Badge>
    },
    {
      key: 'id', title: 'Thao tác', width: '120px',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button size="sm" variant="secondary" icon={<Edit2 size={13} />} onClick={() => openEdit(row)}>Sửa</Button>
          {row.is_active &&
            <Button size="sm" variant="ghost" icon={<Lock size={13} />} onClick={() => handleDeactivate(row)} />}
        </div>
      )
    },
  ];

  return (
    <>
      <div className={styles.toolbar}>
        <div className={styles.searchWrap}>
          <Search size={15} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            placeholder="Tìm kiếm giáo viên..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <Button icon={<UserPlus size={16} />} onClick={openCreate}>
          Thêm giáo viên
        </Button>
      </div>

      <Card>
        <CardBody noPadding>
          <Table
            columns={columns}
            data={loading ? [] : filtered}
            emptyText={loading ? 'Đang tải...' : 'Không có giáo viên nào'}
          />
        </CardBody>
      </Card>

      <Modal
        isOpen={modalOpen}
        onClose={closeModal}
        title={editItem ? 'Chỉnh sửa giáo viên' : 'Thêm giáo viên mới'}
        size="md"
        footer={
          <>
            <Button variant="secondary" onClick={closeModal}>Huỷ</Button>
            <Button loading={saving} onClick={handleSave} type="submit">
              {editItem ? 'Lưu thay đổi' : 'Tạo mới'}
            </Button>
          </>
        }
      >
        {error && <div style={{ color: 'var(--color-absent)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <form className={styles.formGrid} onSubmit={handleSave}>
          <Input label="Mã nhân viên" name="employee_id" value={form.employee_id} onChange={handleChange}
            placeholder="VD: GV001" required disabled={!!editItem} />
          <Input label="Họ và tên" name="full_name" value={form.full_name} onChange={handleChange}
            placeholder="Nguyễn Văn A" required />
          <Input label="Điện thoại" name="phone" value={form.phone} onChange={handleChange} placeholder="0901..." />
          <Input label="Email" name="email" type="email" value={form.email} onChange={handleChange} placeholder="gv@edu.vn" />
          <Input label={editItem ? 'Mật khẩu mới (để trống nếu không đổi)' : 'Mật khẩu'} name="password"
            type="password" value={form.password} onChange={handleChange}
            placeholder="Tối thiểu 6 ký tự" required={!editItem}
            className={styles.formFull} />
        </form>
      </Modal>
    </>
  );
};

export default Teachers;
