import { useState, useEffect } from 'react';
import { Plus, Search } from 'lucide-react';
import { Card, CardBody } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import { formatDate, formatShift, getCurrentMonth } from '../../../utils/formatters';
import { SESSION_STATUS, SHIFTS } from '../../../utils/constants';
import styles from '../Teachers/Teachers.module.css';

const initForm = { teacher_id: '', salary_rate_id: '', date: '', shift: 'morning', note: '' };

const Sessions = () => {
  const [sessions,  setSessions]  = useState([]);
  const [teachers,  setTeachers]  = useState([]);
  const [rates,     setRates]     = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [month,     setMonth]     = useState(getCurrentMonth());
  const [modalOpen, setModalOpen] = useState(false);
  const [form,      setForm]      = useState(initForm);
  const [saving,    setSaving]    = useState(false);
  const [error,     setError]     = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [se, te, ra] = await Promise.all([
        adminService.getSessions({ month, per_page: 100 }),
        adminService.getTeachers(),
        adminService.getSalaryRates(),
      ]);
      setSessions(se.data?.items || []);
      setTeachers(te.data || []);
      setRates(ra.data || []);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [month]);

  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));
  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.teacher_id || !form.salary_rate_id || !form.date) {
      setError('Vui lòng điền đầy đủ thông tin'); return;
    }
    setSaving(true); setError('');
    try {
      await adminService.createSession({ ...form, teacher_id: +form.teacher_id, salary_rate_id: +form.salary_rate_id });
      setModalOpen(false); load();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi');
    } finally { setSaving(false); }
  };

  const handleCancel = async (s) => {
    if (!window.confirm('Huỷ buổi dạy này?')) return;
    await adminService.cancelSession(s.id);
    load();
  };

  const handleConfirm = async (s) => {
    await adminService.updateSession(s.id, { status: 'confirmed' });
    load();
  };

  const columns = [
    { key: 'date',        title: 'Ngày dạy', render: (v) => formatDate(v) },
    { key: 'teacher_name',title: 'Giáo viên' },
    { key: 'shift',       title: 'Ca',       render: (v) => formatShift(v) },
    { key: 'class_type',  title: 'Lớp' },
    { key: 'salary_amount',title:'Thù lao', render: (v) => v ? v.toLocaleString('vi-VN') + ' đ' : '---' },
    {
      key: 'status', title: 'Trạng thái',
      render: (v) => <Badge color={SESSION_STATUS[v]?.color || 'pending'}>{SESSION_STATUS[v]?.label || v}</Badge>
    },
    {
      key: 'id', title: 'Thao tác', width: '150px',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {row.status === 'pending' &&
            <Button size="sm" variant="primary" onClick={() => handleConfirm(row)}>Duyệt</Button>}
          {row.status !== 'cancelled' &&
            <Button size="sm" variant="ghost" onClick={() => handleCancel(row)}>Huỷ</Button>}
        </div>
      )
    }
  ];

  return (
    <>
      <div className={styles.toolbar}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500, color: 'var(--color-text-secondary)' }}>Tháng:</label>
          <input type="month" value={month} onChange={e => setMonth(e.target.value)}
            style={{ padding: '0.45rem 0.875rem', border: '1.5px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-family)' }} />
        </div>
        <Button icon={<Plus size={16} />} onClick={() => { setForm(initForm); setError(''); setModalOpen(true); }}>
          Thêm buổi dạy
        </Button>
      </div>

      <Card>
        <CardBody noPadding>
          <Table columns={columns} data={loading ? [] : sessions} emptyText={loading ? 'Đang tải...' : 'Không có buổi dạy nào'} />
        </CardBody>
      </Card>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Thêm buổi dạy" size="md"
        footer={<><Button variant="secondary" onClick={() => setModalOpen(false)}>Huỷ</Button><Button loading={saving} onClick={handleSave}>Tạo buổi dạy</Button></>}>
        {error && <div style={{ color: 'var(--color-absent)', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <form className={styles.formGrid} onSubmit={handleSave}>
          <div className={styles.formFull}>
            <label style={{ display: 'block', fontSize: 'var(--font-size-sm)', fontWeight: 500, marginBottom: '0.375rem', color: 'var(--color-text-secondary)' }}>
              Giáo viên <span style={{ color: 'var(--color-absent)' }}>*</span>
            </label>
            <select name="teacher_id" value={form.teacher_id} onChange={handleChange}
              style={{ width: '100%', padding: '0.5rem 0.875rem', border: '1.5px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-family)', background: 'var(--color-surface)' }}>
              <option value="">-- Chọn giáo viên --</option>
              {teachers.map(t => <option key={t.id} value={t.id}>{t.full_name} ({t.employee_id})</option>)}
            </select>
          </div>
          <div className={styles.formFull}>
            <label style={{ display: 'block', fontSize: 'var(--font-size-sm)', fontWeight: 500, marginBottom: '0.375rem', color: 'var(--color-text-secondary)' }}>
              Mệnh giá / Lớp <span style={{ color: 'var(--color-absent)' }}>*</span>
            </label>
            <select name="salary_rate_id" value={form.salary_rate_id} onChange={handleChange}
              style={{ width: '100%', padding: '0.5rem 0.875rem', border: '1.5px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-family)', background: 'var(--color-surface)' }}>
              <option value="">-- Chọn mệnh giá --</option>
              {rates.map(r => <option key={r.id} value={r.id}>{r.class_type} — {r.amount?.toLocaleString('vi-VN')} đ</option>)}
            </select>
          </div>
          <Input label="Ngày dạy" name="date" type="date" value={form.date} onChange={handleChange} required />
          <div>
            <label style={{ display: 'block', fontSize: 'var(--font-size-sm)', fontWeight: 500, marginBottom: '0.375rem', color: 'var(--color-text-secondary)' }}>Ca dạy</label>
            <select name="shift" value={form.shift} onChange={handleChange}
              style={{ width: '100%', padding: '0.5rem 0.875rem', border: '1.5px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-family)', background: 'var(--color-surface)' }}>
              {Object.entries(SHIFTS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <Input label="Ghi chú" name="note" value={form.note} onChange={handleChange} placeholder="Ghi chú..." className={styles.formFull} />
        </form>
      </Modal>
    </>
  );
};

export default Sessions;
