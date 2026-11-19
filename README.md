# Dashboard Deteksi Topi dan Dasi

Frontend React/Vite untuk demonstrasi dashboard pemantauan atribut sekolah. Versi ini berjalan sepenuhnya di browser dan siap di-deploy sebagai situs statis di Vercel.

## Fitur

- Simulasi status topi dan dasi
- Pergantian hasil demo manual atau otomatis
- Tampilan responsif untuk desktop dan perangkat mobile
- Tanpa backend, database, penyimpanan lokal, kamera, PyTorch, atau YOLO

## Menjalankan secara lokal

```bash
cd frontend
npm install
npm run dev
```

Buka `http://localhost:5173`.

## Build production

```bash
cd frontend
npm run build
```

Hasil build tersedia di `frontend/dist`.

## Deploy ke Vercel

Import repository ini melalui dashboard Vercel. Konfigurasi build telah tersedia pada `vercel.json` sehingga tidak memerlukan environment variable atau layanan eksternal.
