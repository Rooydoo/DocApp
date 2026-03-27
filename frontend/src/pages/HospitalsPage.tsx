import { useState, useEffect } from 'react'
import { hospitalApi, Hospital } from '../api/client'

function HospitalsPage() {
  const [hospitals, setHospitals] = useState<Hospital[]>([])
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Hospital | null>(null)
  const [form, setForm] = useState({
    name: '',
    address: '',
    capacity: 0,
    allows_external: true,
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    const res = await hospitalApi.getAll()
    setHospitals(res.data)
  }

  const openModal = (hospital?: Hospital) => {
    if (hospital) {
      setEditing(hospital)
      setForm({
        name: hospital.name,
        address: hospital.address || '',
        capacity: hospital.capacity,
        allows_external: hospital.allows_external,
      })
    } else {
      setEditing(null)
      setForm({ name: '', address: '', capacity: 0, allows_external: true })
    }
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditing(null)
  }

  const handleSubmit = async () => {
    if (editing) {
      await hospitalApi.update(editing.id, form)
    } else {
      await hospitalApi.create(form)
    }
    closeModal()
    loadData()
  }

  const handleDelete = async (id: number) => {
    if (confirm('削除しますか？')) {
      await hospitalApi.delete(id)
      loadData()
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>病院管理（勤務先）</h2>
      </div>

      <div className="card">
        <div className="action-bar">
          <div></div>
          <button className="btn btn-primary" onClick={() => openModal()}>
            新規登録
          </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>病院名</th>
              <th>住所</th>
              <th>受入人数</th>
              <th>外勤可否</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {hospitals.map((h) => (
              <tr key={h.id}>
                <td>{h.name}</td>
                <td>{h.address}</td>
                <td>{h.capacity}人</td>
                <td>{h.allows_external ? '可' : '不可'}</td>
                <td>
                  <button className="btn btn-secondary btn-sm" onClick={() => openModal(h)}>編集</button>
                  {' '}
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(h.id)}>削除</button>
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
              <h3>{editing ? '病院編集' : '病院登録'}</h3>
              <button onClick={closeModal}>&times;</button>
            </div>

            <div className="form-group">
              <label>病院名</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>

            <div className="form-group">
              <label>住所</label>
              <input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>受入可能人数</label>
                <input
                  type="number"
                  value={form.capacity}
                  onChange={(e) => setForm({ ...form, capacity: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div className="form-group">
                <label>外勤可否</label>
                <select
                  value={form.allows_external ? 'true' : 'false'}
                  onChange={(e) => setForm({ ...form, allows_external: e.target.value === 'true' })}
                >
                  <option value="true">可</option>
                  <option value="false">不可</option>
                </select>
              </div>
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

export default HospitalsPage
