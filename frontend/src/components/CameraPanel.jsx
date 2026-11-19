import { Camera, RefreshCcw } from 'lucide-react'

export default function CameraPanel({ cameraUrl, loading, onDetect, autoDetect, setAutoDetect }) {
  const streamUrl = cameraUrl?.replace('/capture', '/stream')

  return (
    <section className="card camera-card">
      <div className="card-title">
        <div>
          <h2>Live Kamera</h2>
          <p>Stream ESP32 tampil langsung; status YOLO diperbarui otomatis setelah setiap frame diproses.</p>
        </div>
        <Camera />
      </div>

      <div className="camera-frame">
        {streamUrl ? (
          <img src={streamUrl} alt="Live stream ESP32" />
        ) : (
          <div className="empty-camera">
            <Camera size={48} />
            <p>Menghubungkan ke kamera...</p>
          </div>
        )}
      </div>

      <div className="actions">
        <button onClick={onDetect} disabled={loading}>
          <RefreshCcw size={16} />
          {loading ? 'Memproses...' : 'Deteksi Sekarang'}
        </button>
        <label className="toggle">
          <input
            type="checkbox"
            checked={autoDetect}
            onChange={(e) => setAutoDetect(e.target.checked)}
          />
          Deteksi real-time
        </label>
      </div>
    </section>
  )
}
