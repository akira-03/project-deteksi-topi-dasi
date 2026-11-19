import { CameraOff, Radio, WifiOff } from 'lucide-react'

export default function CameraPanel() {
  return (
    <section className="card camera-card">
      <div className="card-title">
        <div>
          <span className="eyebrow"><Radio size={13} /> LIVE MONITOR</span>
          <h2>Kamera Utama</h2>
          <p>Area pemantauan video real-time.</p>
        </div>
        <span className="status-pill offline"><span className="status-dot" /> OFFLINE</span>
      </div>

      <div className="camera-frame offline-frame">
        <div className="frame-grid" />
        <div className="corner top-left" />
        <div className="corner top-right" />
        <div className="corner bottom-left" />
        <div className="corner bottom-right" />
        <div className="camera-off-state">
          <span className="camera-icon"><CameraOff size={42} /></span>
          <h3>Kamera tidak aktif</h3>
          <p>Hubungkan sumber kamera untuk memulai pemantauan.</p>
          <span className="connection-note"><WifiOff size={14} /> Tidak ada sinyal video</span>
        </div>
        <span className="frame-time">--:--:--</span>
        <span className="frame-quality">NO SIGNAL</span>
      </div>

      <div className="camera-meta">
        <span><small>Sumber</small>Belum terhubung</span>
        <span><small>Resolusi</small>—</span>
        <span><small>Frame rate</small>0 FPS</span>
      </div>
    </section>
  )
}
