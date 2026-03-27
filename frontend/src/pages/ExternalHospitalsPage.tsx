import { useState, useEffect } from 'react'
import { externalHospitalApi, ExternalHospital } from '../api/client'

function ExternalHospitalsPage() {
  const [hospitals, setHospitals] = useState<ExternalHospital[]>([])
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<ExternalHospital | null>(null)
  const [form, setForm] = useState({ name: '', address: '' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    const res = await externalHospitalApi.getAll()
    setHospitals(res.data)
  }

  const openModal = (hospital?: ExternalHospital) => {
    if (hospital) {
      setEditing(hospital)
      setForm({ name: hospital.name, address: hospital.address || '' })
    } else {
      setEditing(null)
      setForm({ name: '', address: '' })
    }
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditing(null)
  }

  const handleSubmit = async () => {
    if (editing) {
      await externalHospitalApi.update(editing.id, form)
    } else {
      await externalHospitalApi.create(form)
    }
    closeModal()
    loadData()
  }

  const handleDelete = async (id: number) => {
    if (confirm('削除しますか？')) {
      await externalHospitalApi.delete(id)
      loadData()
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>外勤病院管理</h2>
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
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {hospitals.map((h) => (
              <tr key={h.id}>
                <td>{h.name}</td>
                <td>{h.address}</td>
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
              <h3>{editing ? '外勤病院編集' : '外勤病院登録'}</h3>
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

export default ExternalHospitalsPage
