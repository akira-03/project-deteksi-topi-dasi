import { Camera, ShieldCheck, Sparkles } from 'lucide-react'

export default function Header({ currentTime }) {
  return (
    <header className="header">
      <div className="header-glow" />
      <div className="header-copy">
        <div className="badge"><Sparkles size={15}/> SMART SCHOOL MONITORING</div>
        <h1>Monitoring <span>Topi & Dasi</span></h1>
        <p>Pantau kelengkapan atribut siswa secara real-time melalui satu dashboard yang ringkas dan modern.</p>
      </div>
      <div className="header-card">
        <span className="shield"><ShieldCheck size={28}/></span>
        <div><small>SYSTEM STATUS</small><strong>Standby</strong></div>
        <span className="header-date">{currentTime?.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
        <Camera className="header-camera" size={70} />
      </div>
    </header>
  )
}
