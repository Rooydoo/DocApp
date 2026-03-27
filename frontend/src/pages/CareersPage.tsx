import { useState, useEffect } from 'react'
import { careerApi, staffApi, hospitalApi, periodApi, Career, StaffOption, Hospital, PeriodOption } from '../api/client'

function CareersPage() {
  const [careers, setCareers] = useState<Career[]>([])
  const [staffOptions, setStaffOptions] = useState<StaffOption[]>([])
  const [hospitals, setHospitals] = useState<Hospital[]>([])
  const [periods, setPeriods] = useState<PeriodOption[]>([])
  const [selectedStaff, setSelectedStaff] = useState<number | ''>('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Career | null>(null)
  const [form, setForm] = useState({
    staff_id: 0,
    period: '',
    hospital_id: '' as number | '',
    hospital_name_manual: '',
    notes: '',
  })

  useEffect(() => {
    loadMaster()
  }, [])

  useEffect(() => {
    loadCareers()
  }, [selectedStaff])

  const loadMaster = async () => {
    const [staffRes, hospRes, periodRes] = await Promise.all([
      staffApi.getOptions(),
      hospitalApi.getAll(),
      periodApi.getAll(),
    ])
    setStaffOptions(staffRes.data)
    setHospitals(hospRes.data)
    setPeriods(periodRes.data)
  }

  const loadCareers = async () => {
    const res = await careerApi.getAll(selectedStaff || undefined)
    setCareers(res.data)
  }

  const openModal = (career?: Career) => {
    if (career) {
      setEditing(career)
      setForm({
        staff_id: career.staff_id,
        period: career.period,
        hospital_id: career.hospital_id || '',
        hospital_name_manual: career.hospital_name_manual || '',
        notes: career.notes || '',
      })
    } else {
      setEditing(null)
      setForm({
        staff_id: selectedStaff || 0,
        period: '',
        hospital_id: '',
        hospital_name_manual: '',
        notes: '',
      })
    }
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditing(null)
  }

  const handleSubmit = async () => {
    const data = {
      ...form,
      hospital_id: form.hospital_id || undefined,
    }

    if (editing) {
      await careerApi.update(editing.id, data)
    } else {
      await careerApi.create(data)
    }
    closeModal()
    loadCareers()
  }

  const handleDelete = async (id: number) => {
    if (confirm('削除しますか？')) {
      await careerApi.delete(id)
      loadCareers()
    }
  }

  const getStaffName = (id: number) => {
    const s = staffOptions.find((s) => s.id === id)
    return s?.display_name || ''
  }

  return (
    <div>
      <div className="page-header">
        <h2>経歴管理</h2>
      </div>

      <div className="card">
        <div className="action-bar">
          <div className="filters">
            <select
              value={selectedStaff}
              onChange={(e) => setSelectedStaff(e.target.value ? parseInt(e.target.value) : '')}
            >
              <option value="">全員</option>
              {staffOptions.map((s) => (
                <option key={s.id} value={s.id}>{s.display_name}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={() => openModal()}>
            新規登録
          </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>職員</th>
              <th>期間</th>
              <th>配置先</th>
              <th>備考</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {careers.map((c) => (
              <tr key={c.id}>
                <td>{getStaffName(c.staff_id)}</td>
                <td>{c.period}</td>
                <td>{c.hospital_display}</td>
                <td>{c.notes}</td>
                <td>
                  <button className="btn btn-secondary btn-sm" onClick={() => openModal(c)}>編集</button>
                  {' '}
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(c.id)}>削除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editing ? '経歴編集' : '経歴登録'}</h3>
              <button onClick={closeModal}>&times;</button>
            </div>

            <div className="form-group">
              <label>職員</label>
              <select
                value={form.staff_id}
                onChange={(e) => setForm({ ...form, staff_id: parseInt(e.target.value) })}
              >
                <option value={0}>選択してください</option>
                {staffOptions.map((s) => (
                  <option key={s.id} value={s.id}>{s.display_name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>期間</label>
              <select
                value={form.period}
                onChange={(e) => setForm({ ...form, period: e.target.value })}
              >
                <option value="">選択してください</option>
                {periods.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>配置先病院</label>
              <select
                value={form.hospital_id}
                onChange={(e) => setForm({ ...form, hospital_id: e.target.value ? parseInt(e.target.value) : '' })}
              >
                <option value="">入局前（自由入力）</option>
                {hospitals.map((h) => (
                  <option key={h.id} value={h.id}>{h.name}</option>
                ))}
              </select>
            </div>

            {form.hospital_id === '' && (
              <div className="form-group">
                <label>配置先（入局前）</label>
                <input
                  value={form.hospital_name_manual}
                  onChange={(e) => setForm({ ...form, hospital_name_manual: e.target.value })}
                  placeholder="他大学病院名など"
                />
              </div>
            )}

            <div className="form-group">
              <label>備考</label>
              <textarea
                rows={2}
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
              />
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={closeModal}>キャンセル</button>
              <button className="btn btn-primary" onClick={handleSubmit}>保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CareersPage
