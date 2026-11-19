import { Download } from 'lucide-react'
import { downloadLogUrl } from '../services/api'

export default function DetectionTable({ detections }) {
  return (
    <section className="card full-width">
      <div className="card-title">
        <div>
          <h2>Detail Objek Terdeteksi</h2>
          <p>Daftar bounding box yang dibaca oleh model YOLO.</p>
        </div>
        <a className="download" href={downloadLogUrl()} target="_blank" rel="noreferrer">
          <Download size={16} /> Download Log CSV
        </a>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>No</th>
              <th>Class</th>
              <th>Confidence</th>
              <th>Bounding Box</th>
            </tr>
          </thead>
          <tbody>
            {detections?.length ? detections.map((item, index) => (
              <tr key={`${item.class}-${index}`}>
                <td>{index + 1}</td>
                <td>{item.class}</td>
                <td>{Math.round(item.confidence * 100)}%</td>
                <td>{item.xmin}, {item.ymin}, {item.xmax}, {item.ymax}</td>
              </tr>
            )) : (
              <tr>
                <td colSpan="4" className="empty-row">Belum ada objek terdeteksi.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
