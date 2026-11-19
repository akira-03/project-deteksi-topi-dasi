import { useEffect, useRef, useState } from 'react'
import Header from './components/Header'
import CameraPanel from './components/CameraPanel'
import DetectionStatus from './components/DetectionStatus'
import DetectionTable from './components/DetectionTable'
import { getHealth, runDetection } from './services/api'

export default function App() {
  const [health, setHealth] = useState(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [autoDetect, setAutoDetect] = useState(true)
  const detectionInProgress = useRef(false)

  async function detect() {
    if (detectionInProgress.current || !health?.esp32_capture_url) return

    try {
      detectionInProgress.current = true
      setLoading(true)
      setError('')
      const result = await runDetection(health?.esp32_capture_url)
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      detectionInProgress.current = false
      setLoading(false)
    }
  }

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null))
  }, [])

  useEffect(() => {
    if (!autoDetect || !health?.esp32_capture_url) return

    let stopped = false
    let timer

    async function nextDetection() {
      await detect()
      if (!stopped) timer = setTimeout(nextDetection, 750)
    }

    nextDetection()
    return () => {
      stopped = true
      clearTimeout(timer)
    }
  }, [autoDetect, health?.esp32_capture_url])

  return (
    <main className="page">
      <Header />

      {error && <div className="error">{error}</div>}

      <div className="system-info">
        <span>Backend: {health?.ok ? 'Aktif' : 'Belum terhubung'}</span>
        <span>Model best.pt: {health?.model_exists ? 'Ada' : 'Belum ada'}</span>
        <span>ESP32: {health?.esp32_capture_url || 'Belum dicek'}</span>
      </div>

      <div className="grid">
        <CameraPanel
          cameraUrl={health?.esp32_capture_url}
          loading={loading}
          onDetect={detect}
          autoDetect={autoDetect}
          setAutoDetect={setAutoDetect}
        />
        <DetectionStatus data={data} />
        <DetectionTable detections={data?.detections || []} />
      </div>
    </main>
  )
}
