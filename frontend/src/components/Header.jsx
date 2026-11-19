import { Camera, ShieldCheck } from 'lucide-react'

export default function Header() {
  return (
    <header className="header">
      <div>
        <div className="badge"><Camera size={16}/> ESP32-S3 Camera AI</div>
        <h1>Monitoring Kelengkapan Topi dan Dasi</h1>
        <p>Dashboard deteksi perlengkapan sekolah berbasis kamera ESP32-S3 dan YOLO.</p>
      </div>
      <div className="header-card">
        <ShieldCheck size={28}/>
        <span>Sistem Monitoring</span>
      </div>
    </header>
  )
}
