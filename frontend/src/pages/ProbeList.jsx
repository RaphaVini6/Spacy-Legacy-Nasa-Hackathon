import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProbes } from '../services/api'
import { DESTINATIONS, STATUS } from '../labels'

export default function ProbeList() {
  const [probes, setProbes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [destination, setDestination] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    getProbes()
      .then(setProbes)
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [])

  const filtered = probes.filter(
    (p) =>
      (!destination || p.destination === destination) &&
      `${p.name} ${p.mission} ${p.location}`.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <>
      <div className="filters">
        <input type="search" placeholder="Search by name, mission or place" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={destination} onChange={(e) => setDestination(e.target.value)}>
          <option value="">All destinations</option>
          {Object.entries(DESTINATIONS).map(([key, label]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="error">Could not load the data.</p>}
      {!loading && !error && <p className="muted">{filtered.length} items</p>}

      <ul className="grid">
        {filtered.map((p) => (
          <li key={p.id} className="card">
            <Link to={`/probes/${p.id}`}>
              {p.imageUrl && <img src={p.imageUrl} alt="" loading="lazy" />}
              <strong>{p.name}</strong>
              <span className="muted">
                {p.mission} - {DESTINATIONS[p.destination]} - {p.date.slice(0, 4)}
              </span>
              <span className={`status status-${p.status}`}>{STATUS[p.status]}</span>
            </Link>
          </li>
        ))}
      </ul>
    </>
  )
}
