import { useState } from 'react'
import axios from 'axios'
import { Wand2, Download, Loader2 } from 'lucide-react'

function App() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!topic) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Netlify üzerinden proxy veya lokal API çağrısı
      const response = await axios.post('http://127.0.0.1:8001/api/generate', { topic })
      setResult(response.data)
    } catch (err) {
      console.error(err)
      setError("Video üretilirken bir hata oluştu. Lütfen tekrar deneyin.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Faceless Video Bot 🎬</h1>
        <p>Yapay zeka ile anında TikTok ve Reels videoları üretin.</p>
      </div>

      <form onSubmit={handleGenerate}>
        <div className="form-group">
          <label>Videonuzun Konusu Ne Olsun?</label>
          <input
            type="text"
            placeholder="Örn: Roma İmparatorluğu'nun Çöküşü"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
          />
        </div>

        <button type="submit" className="generate-btn" disabled={!topic || loading}>
          {loading ? (
            <>
              <Loader2 className="loading-spinner" /> Video Üretiliyor (1-2 Dk Sürebilir)...
            </>
          ) : (
            <>
              <Wand2 /> Videoyu Oluştur
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="result-box" style={{ borderColor: '#ff4444', background: 'rgba(255,68,68,0.1)' }}>
          <p style={{ color: '#ff6666' }}>{error}</p>
        </div>
      )}

      {result && (
        <div className="result-box">
          <h3 style={{ marginBottom: '15px', color: '#00ff88' }}>Videonuz Hazır! 🎉</h3>
          <p><strong>Yapay Zeka Senaryosu:</strong><br/> "{result.script}"</p>
          
          <a href={`http://127.0.0.1:8001${result.video_url}`} download className="download-btn">
            <Download style={{ verticalAlign: 'middle', marginRight: '8px' }} />
            MP4 Olarak İndir
          </a>
        </div>
      )}
    </div>
  )
}

export default App
