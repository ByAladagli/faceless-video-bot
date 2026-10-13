import { useState } from 'react'
import axios from 'axios'
import { Wand2, Download, Loader2 } from 'lucide-react'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001').replace(/\/$/, '')

function App() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async (e) => {
    e.preventDefault()
    const text = topic.trim()
    if (!text) {
      setError('Lütfen videoda seslendirilecek metni girin.')
      return
    }
    if (text.length > 2000) {
      setError('Metin en fazla 2.000 karakter olabilir.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await axios.post(`${API_BASE}/api/generate`, { topic: text }, { timeout: 300000 })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Video üretilemedi. API sunucusunun ve FFmpeg kurulumunun çalıştığını kontrol edin.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Faceless Video Bot</h1>
        <p>Metni Türkçe seslendirme, altyazı ve dikey video haline dönüştürün.</p>
      </div>

      <form onSubmit={handleGenerate}>
        <div className="form-group">
          <label>Videoda seslendirilecek metin</label>
          <textarea
            rows={6}
            maxLength={2000}
            placeholder="Örn: Roma İmparatorluğu'nun çöküşünü anlatan kısa metin..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
          />
          <small>{topic.length}/2000 karakter. Bu prototip senaryo yazmaz; girdiğiniz metni seslendirir.</small>
        </div>

        <button type="submit" className="generate-btn" disabled={!topic.trim() || loading}>
          {loading ? (
            <><Loader2 className="loading-spinner" /> Video oluşturuluyor; render sürebilir...</>
          ) : (
            <><Wand2 /> Videoyu Oluştur</>
          )}
        </button>
      </form>

      {error && (
        <div className="result-box" role="alert" style={{ borderColor: '#ff4444', background: 'rgba(255,68,68,0.1)' }}>
          <p style={{ color: '#ff6666' }}>{error}</p>
        </div>
      )}

      {result && (
        <div className="result-box">
          <h3 style={{ marginBottom: '15px', color: '#00ff88' }}>Video hazır</h3>
          <p><strong>Seslendirilen metin:</strong><br />{result.script}</p>
          <p>{result.notice}</p>
          <a href={`${API_BASE}${result.video_url}`} download className="download-btn">
            <Download style={{ verticalAlign: 'middle', marginRight: '8px' }} />
            MP4 Olarak İndir
          </a>
        </div>
      )}
    </div>
  )
}

export default App
