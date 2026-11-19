import { Camera, RefreshCcw } from 'lucide-react'

export default function CameraPanel({ loading, onDetect, autoDetect, setAutoDetect }) {
  return (
    <section className="card camera-card">
      <div className="card-title">
        <div>
          <h2>Pratinjau Demo</h2>
          <p>Simulasi antarmuka berjalan sepenuhnya di browser tanpa kamera atau server.</p>
        </div>
        <Camera />
      </div>

      <div className="camera-frame">
        <div className="demo-person" aria-label="Ilustrasi siswa untuk mode demo">
          <span className="demo-hat" />
          <span className="demo-head" />
          <span className="demo-body" />
          <span className="demo-tie" />
          <span className="demo-label demo-label-hat">topi</span>
          <span className="demo-label demo-label-tie">dasi</span>
        </div>
      </div>

      <div className="actions">
        <button onClick={onDetect} disabled={loading}>
          <RefreshCcw size={16} />
          {loading ? 'Memuat...' : 'Ganti Hasil Demo'}
        </button>
        <label className="toggle">
          <input
            type="checkbox"
            checked={autoDetect}
            onChange={(e) => setAutoDetect(e.target.checked)}
          />
          Simulasi otomatis
        </label>
      </div>
    </section>
  )
}
