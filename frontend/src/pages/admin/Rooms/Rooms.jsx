import { useState, useEffect } from 'react';
import { Plus, Search, Edit2, Columns, Settings, Box, AlertCircle, Building2, Trash2 } from 'lucide-react';
import { Card, CardBody } from '../../../components/ui/Card';
import Table from '../../../components/ui/Table';
import Badge from '../../../components/ui/Badge';
import Button from '../../../components/ui/Button';
import Modal from '../../../components/ui/Modal';
import Input from '../../../components/ui/Input';
import { adminService } from '../../../services/adminService';
import styles from './Rooms.module.css';

const initForm = { room_name: '', room_number: '', capacity: '', equipment: '', location: '', status: 'available' };

const Rooms = () => {
  const [rooms, setRooms] = useState([]);
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
      const res = await adminService.getRooms();
      setRooms(res.data || []);
    } catch(e) {
      console.error(e);
      setRooms([]);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    const q = search.toLowerCase();
    setFiltered(rooms.filter(r =>
      r.room_name?.toLowerCase().includes(q) ||
      r.location?.toLowerCase().includes(q)
    ));
  }, [search, rooms]);

  const openCreate = () => { setEditItem(null); setForm(initForm); setError(''); setModalOpen(true); };
  const openEdit   = (r)  => { setEditItem(r); setForm(r); setError(''); setModalOpen(true); };
  const closeModal = ()   => { setModalOpen(false); setError(''); };

  const handleChange = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.room_name || !form.capacity) {
      setError('Vui lòng nhập tên phòng và sức chứa'); return;
    }
    
    setSaving(true);
    setError('');
    
    // Convert capacity to integer
    const payload = { ...form, capacity: parseInt(form.capacity) || 0 };
    
    try {
      if (editItem) {
        await adminService.updateRoom(editItem.id, payload);
      } else {
        await adminService.createRoom(payload);
      }
      closeModal();
      load();
    } catch (err) {
      setError(err.response?.data?.message || 'Đã xảy ra lỗi');
    } finally { setSaving(false); }
  };

  const handleDelete = async (e, roomId, roomName) => {
    e.stopPropagation();
    if (!window.confirm(`Bạn có chắc muốn xoá phòng học "${roomName}"?`)) return;
    try {
      await adminService.deleteRoom(roomId);
      load();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi khi xoá phòng');
    }
  };

  const getStatusBadge = (status) => {
    if(status === 'available') return <Badge color="present">Hoạt động</Badge>;
    if(status === 'maintenance') return <Badge color="late">Bảo trì</Badge>;
    if(status === 'occupied') return <Badge color="absent">Đang sử dụng</Badge>;
    return <Badge color="absent">Không rõ</Badge>;
  };

  const columns = [
    {
      key: 'room_name', title: 'Tên phòng',
      render: (v, row) => (
        <div className={styles.nameCell}>
          <div className={styles.iconBox}><Building2 size={16} /></div>
          <div>
            <div className={styles.roomName}><strong>{v}</strong></div>
            <div className={styles.roomLocation}>{row.location || 'Chưa có vị trí'}</div>
          </div>
        </div>
      )
    },
    { key: 'capacity',  title: 'Sức chứa', render: (v) => `${v} người` },
    { key: 'equipment',  title: 'Trang thiết bị' },
    {
      key: 'status', title: 'Trạng thái',
      render: (v) => getStatusBadge(v)
    },
    {
      key: 'id', title: 'Thao tác', width: '120px',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button size="sm" variant="secondary" icon={<Edit2 size={13} />} onClick={() => openEdit(row)}>Sửa</Button>
          <Button size="sm" variant="ghost" icon={<Trash2 size={13} color="var(--color-absent)" />} onClick={(e) => handleDelete(e, row.id, row.room_name)} />
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
            placeholder="Tìm kiếm phòng học..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <Button icon={<Plus size={16} />} onClick={openCreate}>
          Thêm phòng mới
        </Button>
      </div>

      <Card>
        <CardBody noPadding>
          <Table
            columns={columns}
            data={loading ? [] : filtered}
            emptyText={loading ? 'Đang tải...' : 'Không có phòng học nào'}
          />
        </CardBody>
      </Card>

      <Modal
        isOpen={modalOpen}
        onClose={closeModal}
        title={editItem ? 'Chỉnh sửa phòng học' : 'Thêm phòng học mới'}
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
          <Input label="Tên phòng" name="room_name" value={form.room_name} onChange={handleChange}
            placeholder="VD: Phòng 101" required />
            
          <Input label="Sức chứa (người)" name="capacity" type="number" value={form.capacity} onChange={handleChange}
            placeholder="VD: 30" required />
            
          <Input label="Tầng / Vị trí" name="location" value={form.location} onChange={handleChange}
            placeholder="Tầng 1 - Khu A" className={styles.formFull} />
            
          <Input label="Trang thiết bị" name="equipment" value={form.equipment} onChange={handleChange}
            placeholder="Máy chiếu, Bảng từ, TV..." className={styles.formFull} />
            
          {editItem && (
            <div style={{ gridColumn: '1 / -1', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-text)' }}>Trạng thái</label>
              <select 
                name="status" 
                value={form.status} 
                onChange={handleChange}
                style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '0.875rem' }}
              >
                <option value="available">Hoạt động (Có sẵn)</option>
                <option value="maintenance">Bảo trì</option>
                <option value="occupied">Đang sử dụng</option>
              </select>
            </div>
          )}
        </form>
      </Modal>
    </>
  );
};

export default Rooms;
