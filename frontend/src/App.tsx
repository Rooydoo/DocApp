import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import StaffPage from './pages/StaffPage'
import HospitalsPage from './pages/HospitalsPage'
import ExternalHospitalsPage from './pages/ExternalHospitalsPage'
import CareersPage from './pages/CareersPage'
import ExternalWorkByStaffPage from './pages/ExternalWorkByStaffPage'
import ExternalWorkByHospitalPage from './pages/ExternalWorkByHospitalPage'
import ShiftViewPage from './pages/ShiftViewPage'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <aside className="sidebar">
          <h1>医局人員管理</h1>
          <nav>
            <NavLink to="/">職員管理</NavLink>
            <NavLink to="/hospitals">病院管理</NavLink>
            <NavLink to="/external-hospitals">外勤病院</NavLink>
            <NavLink to="/careers">経歴管理</NavLink>
            <NavLink to="/external-work/staff">外勤（職員）</NavLink>
            <NavLink to="/external-work/hospital">外勤（病院）</NavLink>
            <NavLink to="/shift">シフト確認</NavLink>
          </nav>
        </aside>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<StaffPage />} />
            <Route path="/hospitals" element={<HospitalsPage />} />
            <Route path="/external-hospitals" element={<ExternalHospitalsPage />} />
            <Route path="/careers" element={<CareersPage />} />
            <Route path="/external-work/staff" element={<ExternalWorkByStaffPage />} />
            <Route path="/external-work/hospital" element={<ExternalWorkByHospitalPage />} />
            <Route path="/shift" element={<ShiftViewPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
