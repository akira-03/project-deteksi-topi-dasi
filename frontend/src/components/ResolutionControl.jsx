import { useEffect, useState } from 'react'
import { getCameraResolutions, setCameraResolution } from '../services/api'

const FALLBACK_RESOLUTIONS = [
  { name: 'QQVGA', label: 'QQVGA 160x120' },
  { name: 'QVGA', label: 'QVGA 320x240' },
  { name: 'VGA', label: 'VGA 640x480' },
  { name: 'SVGA', label: 'SVGA 800x600' },
  { name: 'XGA', label: 'XGA 1024x768' },
  { name: 'SXGA', label: 'SXGA 1280x1024' },
  { name: 'UXGA', label: 'UXGA 1600x1200' },
]

export default function ResolutionControl() {
  const [resolutions, setResolutions] = useState(FALLBACK_RESOLUTIONS)
  const [selected, setSelected] = useState('VGA')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    getCameraResolutions()
      .then((data) => {
        setResolutions(data.resolutions || FALLBACK_RESOLUTIONS)
        setSelected(data.default || 'VGA')
      })
      .catch(() => {
        setResolutions(FALLBACK_RESOLUTIONS)
        setSelected('VGA')
      })
  }, [])

  async function applyResolution() {
    try {
      setLoading(true)
      setMessage('')
      setError('')
      const result = await setCameraResolution(selected)
      setMessage(result.message || `Resolusi kamera berhasil diubah ke ${selected}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="resolution-control">
      <div>
        <h3>Resolusi Kamera</h3>
        <p>Atur ukuran frame ESP32-S3 dari dashboard.</p>
      </div>

      <div className="resolution-row">
        <select value={selected} onChange={(e) => setSelected(e.target.value)}>
          {resolutions.map((item) => (
            <option key={item.name} value={item.name}>
              {item.label || item.name}
            </option>
          ))}
        </select>
        <button type="button" className="resolution-button" onClick={applyResolution} disabled={loading}>
          {loading ? 'Menerapkan...' : 'Terapkan Resolusi'}
        </button>
      </div>

      {message && <p className="resolution-message success">{message}</p>}
      {error && <p className="resolution-message error-text">{error}</p>}
    </div>
  )
}
