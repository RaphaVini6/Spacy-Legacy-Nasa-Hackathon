import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import SurfaceMap from './SurfaceMap'

// Real surface of the Moon / Mars from NASA Trek (WMTS, equirectangular), like Mars Trek / Moon Trek.
// Zoom levels come from each layer's WMTSCapabilities.xml. Leaflet is used directly (BSD-2) instead of
// react-leaflet, whose Hippocratic license is not an OSI open-source license.
const LAYERS = {
  Moon: {
    url: 'https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/default028mm/{z}/{y}/{x}.jpg',
    maxZoom: 8,
    attribution: '<a href="https://trek.nasa.gov/moon/" target="_blank" rel="noreferrer">NASA Moon Trek</a> · LRO WAC mosaic (NASA/GSFC/ASU)',
  },
  Mars: {
    url: 'https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg',
    maxZoom: 7,
    attribution: '<a href="https://trek.nasa.gov/mars/" target="_blank" rel="noreferrer">NASA Mars Trek</a> · Viking MDIM 2.1 color mosaic (NASA/USGS)',
  },
}
const WORLD = [[-90, -180], [90, 180]]

export default function PlanetMap({ destination, latitude, longitude, label }) {
  const layer = LAYERS[destination]
  const el = useRef(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (!layer || failed || !el.current) return
    const map = L.map(el.current, {
      crs: L.CRS.EPSG4326,
      center: [latitude, longitude],
      zoom: Math.min(4, layer.maxZoom),
      minZoom: 1,
      maxZoom: layer.maxZoom,
      maxBounds: WORLD,
      maxBoundsViscosity: 1,
      scrollWheelZoom: false,
    })
    // without the NASA tiles (offline, Trek down) fall back to the simple drawn map
    let loaded = false
    let errors = 0
    L.tileLayer(layer.url, { attribution: layer.attribution, noWrap: true, bounds: WORLD, maxZoom: layer.maxZoom })
      .on('tileload', () => { loaded = true })
      .on('tileerror', () => {
        errors += 1
        if (!loaded && errors > 4) setFailed(true)
      })
      .addTo(map)
    L.circleMarker([latitude, longitude], { radius: 18, color: '#ffd88a', weight: 2, fill: false, interactive: false, className: 'planet-map-pulse' }).addTo(map)
    const tip = document.createElement('span')
    tip.textContent = label
    L.circleMarker([latitude, longitude], { radius: 9, color: '#000', weight: 2, fillColor: '#f2b84b', fillOpacity: 1 })
      .bindTooltip(tip, { permanent: true, direction: 'top', offset: [0, -10] })
      .addTo(map)
    return () => map.remove()
  }, [layer, failed, latitude, longitude, label])

  if (!layer || failed) return <SurfaceMap destination={destination} latitude={latitude} longitude={longitude} label={label} />
  return <div ref={el} className="planet-map" role="region" aria-label={label} />
}
