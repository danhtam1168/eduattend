import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Layout
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/layout/ProtectedRoute';

// Pages
import Login from './pages/Login/Login';

// Admin Pages
import Dashboard from './pages/admin/Dashboard/Dashboard';
import Teachers from './pages/admin/Teachers/Teachers';
import Students from './pages/admin/Students/Students';
import Classes from './pages/admin/Classes/Classes';
import Rooms from './pages/admin/Rooms/Rooms';
import Schedules from './pages/admin/Schedules/Schedules';
import Sessions from './pages/admin/Sessions/Sessions';
import SalaryReport from './pages/admin/SalaryReport/SalaryReport';
import Settings from './pages/admin/Settings/Settings';

// Teacher Pages
import MySessions from './pages/teacher/MySessions/MySessions';
import MarkAttendance from './pages/teacher/MarkAttendance/MarkAttendance';
import Profile from './pages/teacher/Profile/Profile';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Route */}
        <Route path="/login" element={<Login />} />

        {/* Admin Routes */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="teachers" element={<Teachers />} />
          <Route path="students" element={<Students />} />
          <Route path="classes" element={<Classes />} />
          <Route path="rooms" element={<Rooms />} />
          <Route path="schedules" element={<Schedules />} />
          <Route path="sessions" element={<Sessions />} />
          <Route path="salary-report" element={<SalaryReport />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Teacher Routes */}
        <Route path="/teacher" element={
          <ProtectedRoute allowedRoles={['teacher']}>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="sessions" replace />} />
          <Route path="sessions" element={<MySessions />} />
          <Route path="sessions/:id/attend" element={<MarkAttendance />} />
          <Route path="profile" element={<Profile />} />
        </Route>

        {/* Root Redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        
        {/* 404 Catch all */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
