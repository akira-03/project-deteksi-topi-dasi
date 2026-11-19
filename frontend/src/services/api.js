const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000')
  .replace(/\/$/, '')

export async function getHealth() {
  const response = await fetch(`${API_BASE}/api/health`)
  return response.json()
}

export async function runDetection(cameraUrl) {
  if (!cameraUrl) {
    throw new Error('URL kamera belum tersedia')
  }

  const cameraResponse = await fetch(cameraUrl, { cache: 'no-store' })
  if (!cameraResponse.ok) {
    throw new Error(`Kamera tidak merespons (HTTP ${cameraResponse.status})`)
  }

  const image = await cameraResponse.blob()
  const response = await fetch(`${API_BASE}/api/detect/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'image/jpeg' },
    body: image,
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || 'Gagal menjalankan deteksi')
  }
  return data
}

export function downloadLogUrl() {
  return `${API_BASE}/api/log/download`
}
