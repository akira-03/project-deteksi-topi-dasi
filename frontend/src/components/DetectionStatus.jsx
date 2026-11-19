import { CheckCircle2, XCircle, Activity } from 'lucide-react'

function StatusBox({ title, detected, confidence }) {
  return (
    <div className={`status-box ${detected ? 'ok' : 'bad'}`}>
      {detected ? <CheckCircle2 /> : <XCircle />}
      <div>
        <h3>{title}</h3>
        <p>{detected ? 'Terdeteksi' : 'Tidak Terdeteksi'}</p>
        <small>Confidence: {confidence ? `${Math.round(confidence * 100)}%` : '0%'}</small>
      </div>
    </div>
  )
}

export default function DetectionStatus({ data }) {
  const topi = data?.summary?.topi || { detected: false, confidence: 0 }
  const dasi = data?.summary?.dasi || { detected: false, confidence: 0 }
  const lengkap = data?.status === 'Lengkap'

  return (
    <section className="card">
      <div className="card-title">
        <div>
          <h2>Status Kelengkapan</h2>
          <p>Menentukan apakah siswa lengkap memakai topi dan dasi.</p>
        </div>
        <Activity />
      </div>

      <div className={`main-status ${lengkap ? 'complete' : 'incomplete'}`}>
        {lengkap ? 'LENGKAP' : 'TIDAK LENGKAP'}
      </div>

      <div className="status-grid">
        <StatusBox title="Topi" detected={topi.detected} confidence={topi.confidence} />
        <StatusBox title="Dasi" detected={dasi.detected} confidence={dasi.confidence} />
      </div>

      {data?.timestamp && <p className="timestamp">Terakhir deteksi: {data.timestamp}</p>}
      {data?.fps && <p className="timestamp">FPS proses: {data.fps}</p>}
    </section>
  )
}
