import { Activity, CircleDashed, ScanLine } from 'lucide-react'

function WaitingBox({ title }) {
  return (
    <div className="status-box waiting">
      <CircleDashed />
      <div>
        <h3>{title}</h3>
        <p>Menunggu kamera</p>
        <small>Confidence: —</small>
      </div>
    </div>
  )
}

export default function DetectionStatus({ cameraOnline }) {
  return (
    <section className="card status-card">
      <div className="card-title">
        <div>
          <span className="eyebrow"><Activity size={13} /> DETECTION STATUS</span>
          <h2>Status Kelengkapan</h2>
          <p>Hasil akan tampil saat kamera aktif.</p>
        </div>
        <ScanLine />
      </div>

      <div className="main-status standby">
        <span className="standby-icon"><ScanLine size={24} /></span>
        <div><small>STATUS SAAT INI</small>MENUNGGU KAMERA</div>
      </div>

      <div className="status-grid">
        <WaitingBox title="Topi" />
        <WaitingBox title="Dasi" />
      </div>

      <div className="status-foot">
        <span className={cameraOnline ? 'online-dot' : 'offline-dot'} />
        Sistem deteksi siaga dan belum menerima frame
      </div>
    </section>
  )
}
