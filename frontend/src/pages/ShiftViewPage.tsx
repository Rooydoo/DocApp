import { useState, useEffect } from 'react'
import { staffApi, careerApi, externalWorkApi, periodApi, StaffOption, PeriodOption } from '../api/client'

const DAYS = ['月', '火', '水', '木', '金']
const SLOTS = ['午前', '午後']

function ShiftViewPage() {
  const [staffOptions, setStaffOptions] = useState<StaffOption[]>([])
  const [periods, setPeriods] = useState<PeriodOption[]>([])
  const [selectedStaff, setSelectedStaff] = useState<number | ''>('')
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [baseHospital, setBaseHospital] = useState('')
  const [externalGrid, setExternalGrid] = useState<Record<string, { hospital: string; frequency: string } | null>>({})

  useEffect(() => {
    loadMaster()
  }, [])

  useEffect(() => {
    if (selectedStaff && selectedPeriod) {
      loadData()
    }
  }, [selectedStaff, selectedPeriod])

  const loadMaster = async () => {
    const [staffRes, periodRes] = await Promise.all([
      staffApi.getOptions(),
      periodApi.getAll(),
    ])
    setStaffOptions(staffRes.data)
    setPeriods(periodRes.data)

    const currentRes = await periodApi.getCurrent()
    setSelectedPeriod(currentRes.data.value)
  }

  const loadData = async () => {
    if (!selectedStaff || !selectedPeriod) return

    // 経歴から配置先を取得
    const careersRes = await careerApi.getAll(selectedStaff as number)
    const career = careersRes.data.find((c) => c.period === selectedPeriod)
    setBaseHospital(career?.hospital_display || '未配置')

    // 外勤情報を取得
    const extRes = await externalWorkApi.getByStaff(selectedStaff as number, selectedPeriod)
    const data = extRes.data.grid

    const newGrid: typeof externalGrid = {}
    for (const day of DAYS) {
      for (const slot of SLOTS) {
        const key = `${day}_${slot}`
        const ext = data[key]
        if (ext && ext.external_hospital_id) {
          // TODO: 病院名を取得する必要あり（簡易版ではIDのみ）
          newGrid[key] = {
            hospital: `外勤(${ext.external_hospital_id})`,
            frequency: ext.frequency,
          }
        } else {
          newGrid[key] = null
        }
      }
    }
    setExternalGrid(newGrid)
  }

  const getCell = (day: string, slot: string) => {
    const key = `${day}_${slot}`
    const ext = externalGrid[key]
    if (ext) {
      return (
        <div style={{ background: '#ffeeba', padding: 4, borderRadius: 4 }}>
          <strong>{ext.hospital}</strong>
          <br />
          <small>{ext.frequency}</small>
        </div>
      )
    }
    return baseHospital
  }

  return (
    <div>
      <div className="page-header">
        <h2>シフト確認</h2>
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
        </div>

        {selectedStaff && (
          <>
            <p style={{ marginBottom: 16 }}>
              <strong>配置先:</strong> {baseHospital}
            </p>

            <div className="schedule-grid">
              <div className="header"></div>
              <div className="header">午前</div>
              <div className="header">午後</div>

              {DAYS.map((day) => (
                <>
                  <div key={`${day}-label`} className="day-label">{day}</div>
                  {SLOTS.map((slot) => (
                    <div key={`${day}_${slot}`} className="cell">
                      {getCell(day, slot)}
                    </div>
                  ))}
                </>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default ShiftViewPage
