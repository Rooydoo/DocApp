import axios from 'axios'

const API_BASE = import.meta.env.DEV ? 'http://localhost:9000' : ''

const api = axios.create({
  baseURL: API_BASE,
})

// 型定義
export interface Staff {
  id: number
  last_name: string
  first_name: string
  last_name_kana?: string
  first_name_kana?: string
  position: string
  email?: string
  phone?: string
  join_year?: number
  address?: string
  evaluation_memo?: string
  display_name: string
}

export interface Hospital {
  id: number
  name: string
  address?: string
  capacity: number
  allows_external: boolean
}

export interface ExternalHospital {
  id: number
  name: string
  address?: string
}

export interface Career {
  id: number
  staff_id: number
  period: string
  hospital_id?: number
  hospital_name_manual?: string
  notes?: string
  hospital_display: string
}

export interface ExternalWork {
  id: number
  staff_id: number
  external_hospital_id: number
  day_of_week: string
  time_slot: string
  frequency: string
  period: string
}

export interface StaffOption {
  id: number
  display_name: string
}

export interface PeriodOption {
  value: string
  label: string
}

// API関数
export const staffApi = {
  getAll: () => api.get<Staff[]>('/api/staff'),
  getOptions: () => api.get<StaffOption[]>('/api/staff/options'),
  get: (id: number) => api.get<Staff>(`/api/staff/${id}`),
  create: (data: Omit<Staff, 'id' | 'display_name'>) => api.post<Staff>('/api/staff', data),
  update: (id: number, data: Omit<Staff, 'id' | 'display_name'>) => api.put<Staff>(`/api/staff/${id}`, data),
  delete: (id: number) => api.delete(`/api/staff/${id}`),
}

export const hospitalApi = {
  getAll: () => api.get<Hospital[]>('/api/hospitals'),
  get: (id: number) => api.get<Hospital>(`/api/hospitals/${id}`),
  create: (data: Omit<Hospital, 'id'>) => api.post<Hospital>('/api/hospitals', data),
  update: (id: number, data: Omit<Hospital, 'id'>) => api.put<Hospital>(`/api/hospitals/${id}`, data),
  delete: (id: number) => api.delete(`/api/hospitals/${id}`),
}

export const externalHospitalApi = {
  getAll: () => api.get<ExternalHospital[]>('/api/external-hospitals'),
  get: (id: number) => api.get<ExternalHospital>(`/api/external-hospitals/${id}`),
  create: (data: Omit<ExternalHospital, 'id'>) => api.post<ExternalHospital>('/api/external-hospitals', data),
  update: (id: number, data: Omit<ExternalHospital, 'id'>) => api.put<ExternalHospital>(`/api/external-hospitals/${id}`, data),
  delete: (id: number) => api.delete(`/api/external-hospitals/${id}`),
}

export const careerApi = {
  getAll: (staffId?: number) => api.get<Career[]>('/api/careers', { params: { staff_id: staffId } }),
  get: (id: number) => api.get<Career>(`/api/careers/${id}`),
  create: (data: Omit<Career, 'id' | 'hospital_display'>) => api.post<Career>('/api/careers', data),
  update: (id: number, data: Omit<Career, 'id' | 'hospital_display'>) => api.put<Career>(`/api/careers/${id}`, data),
  delete: (id: number) => api.delete(`/api/careers/${id}`),
}

export const externalWorkApi = {
  getConstants: () => api.get<{
    days_of_week: string[]
    time_slots: string[]
    frequencies: string[]
    max_slots: number
  }>('/api/external-works/constants'),
  getByStaff: (staffId: number, period: string) =>
    api.get(`/api/external-works/by-staff/${staffId}/${period}`),
  getByHospital: (hospitalId: number, period: string) =>
    api.get(`/api/external-works/by-hospital/${hospitalId}/${period}`),
  bulkUpdateByStaff: (data: { staff_id: number; period: string; slots: any[] }) =>
    api.post('/api/external-works/bulk-update-by-staff', data),
  bulkUpdateByHospital: (data: { external_hospital_id: number; period: string; slots: any[] }) =>
    api.post('/api/external-works/bulk-update-by-hospital', data),
}

export const periodApi = {
  getAll: () => api.get<PeriodOption[]>('/api/periods'),
  getCurrent: () => api.get<{ value: string; fiscal_year: number; quarter: number }>('/api/periods/current'),
}

export const positionApi = {
  getAll: () => api.get<string[]>('/api/positions'),
}

export default api
