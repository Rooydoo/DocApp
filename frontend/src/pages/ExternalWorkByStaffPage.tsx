import { useState, useEffect } from 'react'
import { staffApi, externalHospitalApi, externalWorkApi, periodApi, StaffOption, ExternalHospital, PeriodOption } from '../api/client'

const DAYS = ['月', '火', '水', '木', '金']
const SLOTS = ['午前', '午後']

function ExternalWorkByStaffPage() {
  const [staffOptions, setStaffOptions] = useState<StaffOption[]>([])
  const [externalHospitals, setExternalHospitals] = useState<ExternalHospital[]>([])
  const [periods, setPeriods] = useState<PeriodOption[]>([])
  const [frequencies, setFrequencies] = useState<string[]>([])
  const [maxSlots, setMaxSlots] = useState(3)

  const [selectedStaff, setSelectedStaff] = useState<number | ''>('')
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [grid, setGrid] = useState<Record<string, { external_hospital_id: number | null; frequency: string | null }>>({})

  useEffect(() => {
    loadMaster()
  }, [])

  useEffect(() => {
    if (selectedStaff && selectedPeriod) {
      loadGrid()
    }
  }, [selectedStaff, selectedPeriod])

  const loadMaster = async () => {
    const [staffRes, hospRes, periodRes, constRes] = await Promise.all([
      staffApi.getOptions(),
      externalHospitalApi.getAll(),
      periodApi.getAll(),
      externalWorkApi.getConstants(),
    ])
    setStaffOptions(staffRes.data)
    setExternalHospitals(hospRes.data)
    setPeriods(periodRes.data)
    setFrequencies(constRes.data.frequencies)
    setMaxSlots(constRes.data.max_slots)

    // 現在の期間を取得
    const currentRes = await periodApi.getCurrent()
    setSelectedPeriod(currentRes.data.value)
  }

  const loadGrid = async () => {
    if (!selectedStaff || !selectedPeriod) return

    const res = await externalWorkApi.getByStaff(selectedStaff as number, selectedPeriod)
    const data = res.data.grid

    const newGrid: typeof grid = {}
    for (const day of DAYS) {
      for (const slot of SLOTS) {
        const key = `${day}_${slot}`
        newGrid[key] = data[key] || { external_hospital_id: null, frequency: null }
      }
    }
    setGrid(newGrid)
  }

  const handleCellChange = (day: string, slot: string, hospitalId: number | null, frequency: string | null) => {
    const key = `${day}_${slot}`
    setGrid((prev) => ({
      ...prev,
      [key]: { external_hospital_id: hospitalId, frequency },
    }))
  }

  const countSlots = () => {
    return Object.values(grid).filter((v) => v.external_hospital_id !== null).length
  }

  const handleSave = async () => {
    if (!selectedStaff || !selectedPeriod) return

    const slots = Object.entries(grid).map(([key, value]) => {
      const [day, slot] = key.split('_')
      return {
        day_of_week: day,
        time_slot: slot,
        external_hospital_id: value.external_hospital_id,
        frequency: value.frequency,
      }
    })

    await externalWorkApi.bulkUpdateByStaff({
      staff_id: selectedStaff as number,
      period: selectedPeriod,
      slots,
    })

    alert('保存しました')
  }

  return (
    <div>
      <div className="page-header">
        <h2>外勤管理（職員側）</h2>
      </div>

      <div className="card">
        <div className="action-bar">
          <div className="filters">
            <select value={selectedStaff} onChange={(e) => setSelectedStaff(e.target.value ? parseInt(e.target.value) : '')}>
              <option value="">職員を選択</option>
              {staffOptions.map((s) => (
                <option key={s.id} value={s.id}>{s.display_name}</option>
              ))}
            </select>
            <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)}>
              {periods.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
          <div>
            外勤コマ数: {countSlots()}/{maxSlots}
            {' '}
            <button className="btn btn-primary" onClick={handleSave} disabled={!selectedStaff}>
              保存
            </button>
          </div>
        </div>

        {selectedStaff && (
          <div className="schedule-grid">
            <div className="header"></div>
            <div className="header">午前</div>
            <div className="header">午後</div>

            {DAYS.map((day) => (
              <>
                <div key={`${day}-label`} className="day-label">{day}</div>
                {SLOTS.map((slot) => {
                  const key = `${day}_${slot}`
                  const value = grid[key] || { external_hospital_id: null, frequency: null }

                  return (
                    <div key={key} className="cell">
                      <select
                        value={value.external_hospital_id || ''}
                        onChange={(e) => {
                          const hospId = e.target.value ? parseInt(e.target.value) : null
                          handleCellChange(day, slot, hospId, hospId ? (value.frequency || '毎週') : null)
                        }}
                      >
                        <option value="">--なし--</option>
                        {externalHospitals.map((h) => (
                          <option key={h.id} value={h.id}>{h.name}</option>
                        ))}
                      </select>
                      {value.external_hospital_id && (
                        <select
                          value={value.frequency || ''}
                          onChange={(e) => handleCellChange(day, slot, value.external_hospital_id, e.target.value)}
                          style={{ marginTop: 4 }}
                        >
                          {frequencies.map((f) => (
                            <option key={f} value={f}>{f}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  )
                })}
              </>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ExternalWorkByStaffPage
