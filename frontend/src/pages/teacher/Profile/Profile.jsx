import { useState, useEffect } from 'react';
import { Card, CardHeader, CardBody, CardFooter } from '../../../components/ui/Card';
import Input from '../../../components/ui/Input';
import Button from '../../../components/ui/Button';
import useAuthStore from '../../../store/authStore';
import { authService } from '../../../services/authService';
import { teacherService } from '../../../services/teacherService';
import styles from './Profile.module.css';

const Profile = () => {
  const { user, setUser } = useAuthStore();
  
  // Profile Form
  const [profileForm, setProfileForm] = useState({ phone: '', email: '' });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMsg, setProfileMsg] = useState({ type: '', text: '' });

  // Password Form
  const [pwdForm, setPwdForm] = useState({ old_password: '', new_password: '', confirm_password: '' });
  const [savingPwd, setSavingPwd] = useState(false);
  const [pwdMsg, setPwdMsg] = useState({ type: '', text: '' });

  useEffect(() => {
    if (user) {
      setProfileForm({
        phone: user.phone || '',
        email: user.email || ''
      });
    }
  }, [user]);

  const handleProfileChange = (e) => {
    setProfileForm(p => ({ ...p, [e.target.name]: e.target.value }));
    setProfileMsg({ type: '', text: '' });
  };

  const handlePwdChange = (e) => {
    setPwdForm(p => ({ ...p, [e.target.name]: e.target.value }));
    setPwdMsg({ type: '', text: '' });
  };

  const saveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      const res = await teacherService.updateProfile(profileForm);
      setUser(res.data);
      setProfileMsg({ type: 'success', text: 'Cập nhật thông tin thành công' });
    } catch (err) {
      setProfileMsg({ type: 'error', text: err.response?.data?.message || 'Lỗi cập nhật' });
    } finally {
      setSavingProfile(false);
    }
  };

  const savePassword = async (e) => {
    e.preventDefault();
    if (pwdForm.new_password.length < 6) {
      setPwdMsg({ type: 'error', text: 'Mật khẩu mới phải có ít nhất 6 ký tự' });
      return;
    }
    if (pwdForm.new_password !== pwdForm.confirm_password) {
      setPwdMsg({ type: 'error', text: 'Mật khẩu xác nhận không khớp' });
      return;
    }

    setSavingPwd(true);
    try {
      await authService.changePassword(pwdForm.old_password, pwdForm.new_password);
      setPwdMsg({ type: 'success', text: 'Đổi mật khẩu thành công' });
      setPwdForm({ old_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setPwdMsg({ type: 'error', text: err.response?.data?.message || 'Đổi mật khẩu thất bại' });
    } finally {
      setSavingPwd(false);
    }
  };

  return (
    <div className={styles.page}>
      
      {/* Cập nhật thông tin */}
      <Card className="mb-6" style={{ marginBottom: '2rem' }}>
        <CardHeader title="Thông tin cá nhân" />
        <CardBody>
          <div style={{ marginBottom: '1.5rem', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
            <p><strong>Mã nhân viên:</strong> {user?.employee_id}</p>
            <p style={{ marginTop: '0.25rem' }}><strong>Họ và tên:</strong> {user?.full_name}</p>
            <p style={{ marginTop: '0.5rem', fontStyle: 'italic' }}>* Họ tên và Mã NV chỉ có Admin mới được thay đổi.</p>
          </div>

          <form className={styles.form} id="profileForm" onSubmit={saveProfile}>
            {profileMsg.text && (
              <div style={{ color: profileMsg.type === 'success' ? 'var(--color-present)' : 'var(--color-absent)', fontSize: '0.875rem' }}>
                {profileMsg.text}
              </div>
            )}
            <Input label="Số điện thoại" name="phone" value={profileForm.phone} onChange={handleProfileChange} placeholder="0901..." />
            <Input label="Email" name="email" type="email" value={profileForm.email} onChange={handleProfileChange} placeholder="gv@edu.vn" />
          </form>
        </CardBody>
        <CardFooter>
          <Button form="profileForm" type="submit" loading={savingProfile}>Cập nhật thông tin</Button>
        </CardFooter>
      </Card>

      {/* Đổi mật khẩu */}
      <Card>
        <CardHeader title="Đổi mật khẩu" />
        <CardBody>
          <form className={styles.form} id="pwdForm" onSubmit={savePassword}>
            {pwdMsg.text && (
              <div style={{ color: pwdMsg.type === 'success' ? 'var(--color-present)' : 'var(--color-absent)', fontSize: '0.875rem' }}>
                {pwdMsg.text}
              </div>
            )}
            <Input label="Mật khẩu cũ" name="old_password" type="password" value={pwdForm.old_password} onChange={handlePwdChange} required />
            <Input label="Mật khẩu mới" name="new_password" type="password" value={pwdForm.new_password} onChange={handlePwdChange} required />
            <Input label="Xác nhận mật khẩu mới" name="confirm_password" type="password" value={pwdForm.confirm_password} onChange={handlePwdChange} required />
          </form>
        </CardBody>
        <CardFooter>
          <Button form="pwdForm" type="submit" loading={savingPwd} variant="secondary">Đổi mật khẩu</Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Profile;
