import { useState, useEffect } from 'react'
import { staffApi, externalHospitalApi, externalWorkApi, periodApi, StaffOption, ExternalHospital, PeriodOption } from '../api/client'

const DAYS = ['月', '火', '水', '木', '金']
const SLOTS = ['午前', '午後']

function ExternalWorkByHospitalPage() {
  const [staffOptions, setStaffOptions] = useState<StaffOption[]>([])
  const [externalHospitals, setExternalHospitals] = useState<ExternalHospital[]>([])
  const [periods, setPeriods] = useState<PeriodOption[]>([])
  const [frequencies, setFrequencies] = useState<string[]>([])

  const [selectedHospital, setSelectedHospital] = useState<number | ''>('')
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [grid, setGrid] = useState<Record<string, { staff_id: number | null; frequency: string | null }[]>>({})

  useEffect(() => {
    loadMaster()
  }, [])

  useEffect(() => {
    if (selectedHospital && selectedPeriod) {
      loadGrid()
    }
  }, [selectedHospital, selectedPeriod])

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

    const currentRes = await periodApi.getCurrent()
    setSelectedPeriod(currentRes.data.value)
  }

  const loadGrid = async () => {
    if (!selectedHospital || !selectedPeriod) return

    const res = await externalWorkApi.getByHospital(selectedHospital as number, selectedPeriod)
    const data = res.data.grid

    const newGrid: typeof grid = {}
    for (const day of DAYS) {
      for (const slot of SLOTS) {
        const key = `${day}_${slot}`
        // 1人だけ表示（簡易版）
        const entries = data[key] || []
        newGrid[key] = entries.length > 0
          ? [{ staff_id: entries[0].staff_id, frequency: entries[0].frequency }]
          : [{ staff_id: null, frequency: null }]
      }
    }
    setGrid(newGrid)
  }

  const handleCellChange = (day: string, slot: string, staffId: number | null, frequency: string | null) => {
    const key = `${day}_${slot}`
    setGrid((prev) => ({
      ...prev,
      [key]: [{ staff_id: staffId, frequency }],
    }))
  }

  const handleSave = async () => {
    if (!selectedHospital || !selectedPeriod) return

    const slots = Object.entries(grid).map(([key, values]) => {
      const [day, slot] = key.split('_')
      const v = values[0] || { staff_id: null, frequency: null }
      return {
        day_of_week: day,
        time_slot: slot,
        staff_id: v.staff_id,
        frequency: v.frequency,
      }
    })

    await externalWorkApi.bulkUpdateByHospital({
      external_hospital_id: selectedHospital as number,
      period: selectedPeriod,
      slots,
    })

    alert('保存しました')
  }

  return (
    <div>
      <div className="page-header">
        <h2>外勤管理（病院側）</h2>
      </div>

      <div className="card">
        <div className="action-bar">
          <div className="filters">
            <select value={selectedHospital} onChange={(e) => setSelectedHospital(e.target.value ? parseInt(e.target.value) : '')}>
              <option value="">外勤病院を選択</option>
              {externalHospitals.map((h) => (
                <option key={h.id} value={h.id}>{h.name}</option>
              ))}
            </select>
            <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)}>
              {periods.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleSave} disabled={!selectedHospital}>
            保存
          </button>
        </div>

        {selectedHospital && (
          <div className="schedule-grid">
            <div className="header"></div>
            <div className="header">午前</div>
            <div className="header">午後</div>

            {DAYS.map((day) => (
              <>
                <div key={`${day}-label`} className="day-label">{day}</div>
                {SLOTS.map((slot) => {
                  const key = `${day}_${slot}`
                  const values = grid[key] || [{ staff_id: null, frequency: null }]
                  const value = values[0]

                  return (
                    <div key={key} className="cell">
                      <select
                        value={value.staff_id || ''}
                        onChange={(e) => {
                          const sid = e.target.value ? parseInt(e.target.value) : null
                          handleCellChange(day, slot, sid, sid ? (value.frequency || '毎週') : null)
                        }}
                      >
                        <option value="">--なし--</option>
                        {staffOptions.map((s) => (
                          <option key={s.id} value={s.id}>{s.display_name}</option>
                        ))}
                      </select>
                      {value.staff_id && (
                        <select
                          value={value.frequency || ''}
                          onChange={(e) => handleCellChange(day, slot, value.staff_id, e.target.value)}
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

export default ExternalWorkByHospitalPage
