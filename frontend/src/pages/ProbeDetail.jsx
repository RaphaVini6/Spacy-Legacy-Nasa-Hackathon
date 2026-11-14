import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getProbe } from '../services/api'
import { DATE_KIND, DESTINATIONS, STATUS, TYPES } from '../labels'

export default function ProbeDetail() {
  const { id } = useParams()
  const [probe, setProbe] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    getProbe(id)
      .then(setProbe)
      .catch(() => setError(true))
  }, [id])

  if (error) return <p className="error">This item was not found.</p>
  if (!probe) return <p>Loading...</p>

  const rows = [
    ['Equipment', probe.equipment],
    ['Mission', probe.mission],
    ['Destination', DESTINATIONS[probe.destination]],
    ['Type', TYPES[probe.type]],
    ['Launch', probe.launch],
    [DATE_KIND[probe.dateKind], probe.date],
    ['Status', `${STATUS[probe.status]} - ${probe.statusDetail}`],
    ['Location', probe.location],
    ['Coordinates', probe.latitude != null ? `${probe.latitude}, ${probe.longitude}` : '-'],
    ['Reliability', probe.reliability],
  ]

  return (
    <>
      <Link to="/">{'<'} Back</Link>
      <h1>{probe.name}</h1>

      <div className="detail">
        {probe.imageUrl && <img src={probe.imageUrl} alt={probe.name} />}
        <table>
          <tbody>
            {rows.map(([label, value]) => (
              <tr key={label}>
                <th>{label}</th>
                <td>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Scientific goal</h2>
      <p>{probe.function}</p>

      <h2>How it could be reused</h2>
      <p>{probe.mechanicalReuse}</p>

      <h2>Source</h2>
      <p>
        {probe.source.name}
        {probe.source.nssdcaUrl && (
          <>
            {' - '}
            <a href={probe.source.nssdcaUrl} target="_blank" rel="noreferrer">NSSDCA {probe.source.nssdcaId}</a>
          </>
        )}
      </p>
    </>
  )
}
