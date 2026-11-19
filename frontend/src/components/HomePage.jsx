import { ArrowRight, BrainCircuit, Camera, Cpu, Radio, School, ShieldCheck, Sparkles } from 'lucide-react'

export default function HomePage({ onOpenDashboard }) {
  return (
    <section className="home-page">
      <div className="home-hero">
        <div className="home-copy">
          <span className="home-kicker"><School size={16} /> Karya Inovasi SMA 3</span>
          <h2>Sistem Cerdas Pemantauan Kelengkapan Atribut Sekolah</h2>
          <p>
            Alat ini membantu memantau pemakaian topi dan dasi siswa secara otomatis
            menggunakan ESP32-CAM dan model YOLO, dirancang sebagai karya teknologi
            untuk lomba SMA 3.
          </p>
          <div className="home-actions">
            <button type="button" onClick={onOpenDashboard}>
              Buka Dashboard <ArrowRight size={17} />
            </button>
          </div>
        </div>

        <div className="device-visual" aria-label="Ilustrasi alat deteksi topi dan dasi">
          <div className="device-screen">
            <div className="scan-line" />
            <div className="person-figure">
              <span className="figure-hat" />
              <span className="figure-head" />
              <span className="figure-body" />
              <span className="figure-tie" />
            </div>
            <div className="box-label hat-label">topi 94%</div>
            <div className="box-label tie-label">dasi 88%</div>
          </div>
          <div className="device-base">
            <Camera size={24} />
            <div>
              <strong>ESP32-CAM</strong>
              <span>Live vision node</span>
            </div>
          </div>
        </div>
      </div>

      <div className="intro-grid">
        <article className="intro-card">
          <Radio />
          <h3>Kamera Langsung</h3>
          <p>ESP32 mengirim tampilan kamera ke dashboard untuk pemantauan real-time.</p>
        </article>
        <article className="intro-card">
          <BrainCircuit />
          <h3>YOLO Detection</h3>
          <p>Backend memproses gambar dan membaca objek topi serta dasi dari frame kamera.</p>
        </article>
        <article className="intro-card">
          <ShieldCheck />
          <h3>Status Otomatis</h3>
          <p>Dashboard menampilkan status lengkap atau tidak lengkap berdasarkan hasil deteksi.</p>
        </article>
      </div>

      <div className="project-story">
        <div>
          <span className="section-label"><Sparkles size={15} /> Tentang Alat</span>
          <h3>Dirancang untuk membantu pengawasan atribut siswa secara modern.</h3>
        </div>
        <div className="story-steps">
          <span><Camera size={16} /> ESP32-CAM menangkap suasana depan kamera</span>
          <span><Cpu size={16} /> Laptop menjalankan backend dan model deteksi</span>
          <span><ShieldCheck size={16} /> Hasil ditampilkan sebagai status kelengkapan</span>
        </div>
      </div>
    </section>
  )
}
