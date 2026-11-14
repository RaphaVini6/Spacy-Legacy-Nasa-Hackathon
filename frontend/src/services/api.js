import axios from 'axios'

const api = axios.create({ baseURL: `${import.meta.env.VITE_API_URL ?? ''}/api` })

export const getProbes = () => api.get('/probes').then((r) => r.data)
export const getProbe = (id) => api.get(`/probes/${id}`).then((r) => r.data)
