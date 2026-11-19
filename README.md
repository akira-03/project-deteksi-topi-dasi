# Project Deteksi Topi dan Dasi — ESP32-S3 Camera AI

Project ini berisi struktur siap buka di Cursor untuk monitoring kamera ESP32-S3 yang mendeteksi perlengkapan sekolah: **topi** dan **dasi**.

## Alur Sistem

```text
ESP32-S3 Camera AI -> /capture -> Backend Python Flask -> YOLO best.pt -> Frontend React
```

## Langkah 1 — ESP32 Camera

Buka file:

```text
esp32-camera/5_3/5_3.ino
```

Upload ke ESP32-S3 Camera AI memakai Arduino IDE.

Setelah berhasil, cek endpoint:

```text
http://IP_ESP32/capture
```

## Langkah 2 — Letakkan Model

Letakkan hasil training:

```text
backend/models/best.pt
```

## Langkah 3 — Edit IP Kamera

Buka:

```text
backend/config.py
```

Ubah:

```python
ESP32_CAPTURE_URL = "http://192.168.1.25/capture"
```

Sesuaikan dengan IP ESP32 Anda.

## Langkah 4 — Jalankan Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend berjalan di:

```text
http://localhost:5000
```

## Langkah 5 — Jalankan Website

Buka terminal baru:

```bash
cd frontend
npm install
npm run dev
```

Website berjalan di:

```text
http://localhost:5173
```

## Simpan Hasil ke Google Spreadsheet dengan Apps Script

Di Google Spreadsheet, buka **Extensions > Apps Script**, lalu tempel kode berikut:

```javascript
const SHEET_NAME = 'Deteksi';
const HEADERS = [
  'Waktu',
  'Status',
  'Topi Terdeteksi',
  'Dasi Terdeteksi',
  'Confidence Topi',
  'Confidence Dasi',
  'Jumlah Objek'
];

function setupSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getSheetByName(SHEET_NAME)
    || spreadsheet.insertSheet(SHEET_NAME);

  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  } else {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  }

  sheet.getRange(1, 1, 1, HEADERS.length)
    .setFontWeight('bold')
    .setBackground('#1d4ed8')
    .setFontColor('#ffffff');
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, HEADERS.length);

  return sheet;
}

function doPost(e) {
  const sheet = setupSheet();
  const data = JSON.parse(e.postData.contents);

  sheet.appendRow([
    data.timestamp,
    data.status,
    data.topi_detected ? 'Ya' : 'Tidak',
    data.dasi_detected ? 'Ya' : 'Tidak',
    data.topi_confidence,
    data.dasi_confidence,
    data.total_objects
  ]);

  return ContentService
    .createTextOutput(JSON.stringify({ success: true }))
    .setMimeType(ContentService.MimeType.JSON);
`` 

Setelah menempelkan kode, pilih fungsi **`setupSheet`** pada dropdown fungsi di bagian atas editor Apps Script, lalu tekan **Run**. Pada eksekusi pertama, Google akan meminta otorisasi. Setelah diizinkan, tab `Deteksi` beserta header berwarna biru akan dibuat otomatis. Jangan menjalankan `doPost` secara manual karena fungsi tersebut membutuhkan data dari backend.

Pilih **Deploy > New deployment > Web app**. Atur **Execute as: Me** dan **Who has access: Anyone**, kemudian salin URL deployment yang berakhiran `/exec`.

Sebelum menjalankan backend di PowerShell, isi URL tersebut:

```powershell
$env:GOOGLE_APPS_SCRIPT_URL="https://script.google.com/macros/s/DEPLOYMENT_ID/exec"
$env:GOOGLE_LOG_INTERVAL_SECONDS="10"
python backend/run_server.py
```

Tidak diperlukan service account, file JSON, atau ID Spreadsheet di backend. Worksheet `Deteksi` dan header dibuat otomatis. Interval mencegah deteksi otomatis menulis baris duplikat setiap 750 ms. Status konfigurasi dapat dilihat di endpoint `/api/health`.

## Catatan Penting

- Dataset hasil labeling tidak dimasukkan ke ESP32.
- Dataset digunakan untuk training sampai menghasilkan `best.pt`.
- File `best.pt` diletakkan di backend.
- ESP32 hanya menjadi kamera, bukan tempat training.
- Website mengambil hasil deteksi dari backend Python.

## Class Model

Pastikan saat labeling dan training class-nya sama:

```text
topi
dasi
```
