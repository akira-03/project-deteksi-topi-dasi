import { useEffect, useState } from 'react'
import Header from './components/Header'
import CameraPanel from './components/CameraPanel'
import DetectionStatus from './components/DetectionStatus'
import DetectionTable from './components/DetectionTable'

const demoResults = [
  {
    status: 'Lengkap',
    summary: {
      topi: { detected: true, confidence: 0.94 },
      dasi: { detected: true, confidence: 0.88 },
    },
    detections: [
      { class: 'topi', confidence: 0.94, xmin: 132, ymin: 48, xmax: 276, ymax: 126 },
      { class: 'dasi', confidence: 0.88, xmin: 188, ymin: 184, xmax: 226, ymax: 318 },
    ],
  },
  {
    status: 'Tidak Lengkap',
    summary: {
      topi: { detected: true, confidence: 0.91 },
      dasi: { detected: false, confidence: 0 },
    },
    detections: [
      { class: 'topi', confidence: 0.91, xmin: 139, ymin: 52, xmax: 282, ymax: 130 },
    ],
  },
]

export default function App() {
  const [data, setData] = useState(() => ({
    ...demoResults[0],
    timestamp: new Date().toLocaleString('id-ID'),
  }))
  const [loading, setLoading] = useState(false)
  const [autoDetect, setAutoDetect] = useState(true)
  const [demoIndex, setDemoIndex] = useState(0)

  function detect() {
    setLoading(true)
    window.setTimeout(() => {
      const nextIndex = (demoIndex + 1) % demoResults.length
      setDemoIndex(nextIndex)
      setData({
        ...demoResults[nextIndex],
        timestamp: new Date().toLocaleString('id-ID'),
      })
      setLoading(false)
    }, 350)
  }

  useEffect(() => {
    if (!autoDetect) return undefined
    const timer = window.setInterval(detect, 4000)
    return () => window.clearInterval(timer)
  }, [autoDetect, demoIndex])

  return (
    <main className="page">
      <Header />

      <div className="system-info">
        <span>Mode: Demo Vercel</span>
        <span>Backend: Tidak diperlukan</span>
        <span>Data: Simulasi di browser</span>
      </div>

      <div className="grid">
        <CameraPanel
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
