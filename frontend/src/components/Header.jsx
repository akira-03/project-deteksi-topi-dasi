import { Camera, ShieldCheck } from 'lucide-react'

export default function Header() {
  return (
    <header className="header">
      <div>
        <div className="badge"><Camera size={16}/> Demo Dashboard</div>
        <h1>Monitoring Kelengkapan Topi dan Dasi</h1>
        <p>Prototipe pemantauan atribut sekolah yang siap dijalankan sebagai situs statis di Vercel.</p>
      </div>
      <div className="header-card">
        <ShieldCheck size={28}/>
        <span>Sistem Monitoring</span>
      </div>
    </header>
  )
}
