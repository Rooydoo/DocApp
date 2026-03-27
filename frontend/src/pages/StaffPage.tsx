import { useState, useEffect } from 'react'
import { staffApi, positionApi, Staff } from '../api/client'

function StaffPage() {
  const [staffList, setStaffList] = useState<Staff[]>([])
  const [positions, setPositions] = useState<string[]>([])
  const [showModal, setShowModal] = useState(false)
  const [editingStaff, setEditingStaff] = useState<Staff | null>(null)
  const [form, setForm] = useState({
    last_name: '',
    first_name: '',
    last_name_kana: '',
    first_name_kana: '',
    position: '',
    email: '',
    phone: '',
    join_year: '',
    address: '',
    evaluation_memo: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    const [staffRes, posRes] = await Promise.all([
      staffApi.getAll(),
      positionApi.getAll(),
    ])
    setStaffList(staffRes.data)
    setPositions(posRes.data)
  }

  const openModal = (staff?: Staff) => {
    if (staff) {
      setEditingStaff(staff)
      setForm({
        last_name: staff.last_name,
        first_name: staff.first_name,
        last_name_kana: staff.last_name_kana || '',
        first_name_kana: staff.first_name_kana || '',
        position: staff.position,
        email: staff.email || '',
        phone: staff.phone || '',
        join_year: staff.join_year?.toString() || '',
        address: staff.address || '',
        evaluation_memo: staff.evaluation_memo || '',
      })
    } else {
      setEditingStaff(null)
      setForm({
        last_name: '',
        first_name: '',
        last_name_kana: '',
        first_name_kana: '',
        position: positions[0] || '',
        email: '',
        phone: '',
        join_year: '',
        address: '',
        evaluation_memo: '',
      })
    }
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingStaff(null)
  }

  const handleSubmit = async () => {
    const data = {
      ...form,
      join_year: form.join_year ? parseInt(form.join_year) : undefined,
    }

    if (editingStaff) {
      await staffApi.update(editingStaff.id, data)
    } else {
      await staffApi.create(data)
    }

    closeModal()
    loadData()
  }

  const handleDelete = async (id: number) => {
    if (confirm('削除しますか？')) {
      await staffApi.delete(id)
      loadData()
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>職員管理</h2>
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
              <th>氏名</th>
              <th>かな</th>
              <th>職種</th>
              <th>入局年</th>
              <th>連絡先</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {staffList.map((staff) => (
              <tr key={staff.id}>
                <td>{staff.last_name} {staff.first_name}</td>
                <td>{staff.last_name_kana} {staff.first_name_kana}</td>
                <td>{staff.position}</td>
                <td>{staff.join_year}</td>
                <td>{staff.email}</td>
                <td>
                  <button className="btn btn-secondary btn-sm" onClick={() => openModal(staff)}>
                    編集
                  </button>
                  {' '}
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(staff.id)}>
                    削除
                  </button>
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
              <h3>{editingStaff ? '職員編集' : '職員登録'}</h3>
              <button onClick={closeModal}>&times;</button>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>姓</label>
                <input
                  value={form.last_name}
                  onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>名</label>
                <input
                  value={form.first_name}
                  onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>姓（かな）</label>
                <input
                  value={form.last_name_kana}
                  onChange={(e) => setForm({ ...form, last_name_kana: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>名（かな）</label>
                <input
                  value={form.first_name_kana}
                  onChange={(e) => setForm({ ...form, first_name_kana: e.target.value })}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>職種</label>
                <select
                  value={form.position}
                  onChange={(e) => setForm({ ...form, position: e.target.value })}
                >
                  {positions.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>入局年</label>
                <input
                  type="number"
                  value={form.join_year}
                  onChange={(e) => setForm({ ...form, join_year: e.target.value })}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>メール</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>電話番号</label>
                <input
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              </div>
            </div>

            <div className="form-group">
              <label>住所</label>
              <input
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>評価メモ</label>
              <textarea
                rows={3}
                value={form.evaluation_memo}
                onChange={(e) => setForm({ ...form, evaluation_memo: e.target.value })}
              />
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={closeModal}>
                キャンセル
              </button>
              <button className="btn btn-primary" onClick={handleSubmit}>
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default StaffPage
