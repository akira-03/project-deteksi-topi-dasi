import { useEffect, useState } from 'react'
import { Clock3, Radio, Server, WifiOff } from 'lucide-react'
import Header from './components/Header'
import CameraPanel from './components/CameraPanel'
import DetectionStatus from './components/DetectionStatus'
import DetectionTable from './components/DetectionTable'

export default function App() {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = window.setInterval(() => setCurrentTime(new Date()), 1000)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <main className="page">
      <Header currentTime={currentTime} />

      <section className="system-info" aria-label="Status sistem">
        <div className="info-chip live"><Radio size={17} /><span><small>Mode</small>Real-time</span></div>
        <div className="info-chip offline"><WifiOff size={17} /><span><small>Kamera</small>Offline</span></div>
        <div className="info-chip"><Server size={17} /><span><small>Sistem</small>Siap dihubungkan</span></div>
        <div className="info-chip"><Clock3 size={17} /><span><small>Waktu lokal</small>{currentTime.toLocaleTimeString('id-ID')}</span></div>
      </section>

      <div className="grid">
        <CameraPanel />
        <DetectionStatus data={null} cameraOnline={false} />
        <DetectionTable detections={[]} />
      </div>

      <footer>Monitoring Atribut Sekolah <span>•</span> Sistem real-time</footer>
    </main>
  )
}
