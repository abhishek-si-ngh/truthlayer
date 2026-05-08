import React, { useState, useCallback, useRef } from 'react'
import UploadZone from './components/UploadZone'
import ProgressBar from './components/ProgressBar'
import ResultsPanel from './components/ResultsPanel'
import ClaimCard from './components/ClaimCard'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const PHASE = {
  IDLE: 'idle',
  LOADING: 'loading',
  DONE: 'done',
  ERROR: 'error',
}

export default function App() {
  const [file, setFile] = useState(null)
  const [phase, setPhase] = useState(PHASE.IDLE)
  const [status, setStatus] = useState('')
  const [stage, setStage] = useState('parsing')
  const [progress, setProgress] = useState({ current: 0, total: 0 })
  const [claims, setClaims] = useState([])
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  const abortRef = useRef(null)

  const handleFileSelect = useCallback((f) => {
    setFile(f)
    setPhase(PHASE.IDLE)
    setError('')
    setClaims([])
    setSummary(null)
  }, [])

  const handleAnalyze = useCallback(async () => {
    if (!file) return

    setPhase(PHASE.LOADING)
    setError('')
    setClaims([])
    setSummary(null)
    setStage('parsing')
    setStatus('Uploading PDF...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 120000)

      const response = await fetch(`${API_URL}/api/fact-check`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(err.detail || 'Server error')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const json = line.slice(6).trim()
          if (!json) continue

          try {
            const event = JSON.parse(json)
            handleEvent(event)
          } catch {
            // ignore malformed events
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. Please try with a smaller PDF or check your connection.')
      } else {
        setError(err.message || 'Something went wrong. Please try again.')
      }
      setPhase(PHASE.ERROR)
    }
  }, [file])

  const handleEvent = useCallback((event) => {
    switch (event.type) {
      case 'status':
        setStatus(event.message)
        if (event.stage) setStage(event.stage)
        break

      case 'parsed':
        setStatus(event.message)
        setStage('extracting')
        break

      case 'claims_extracted':
        setStatus(event.message)
        setStage('verifying')
        setProgress({ current: 0, total: event.total })
        // Pre-populate with pending claims (no verdict yet)
        setClaims(event.claims.map(c => ({ ...c, verdict: null })))
        break

      case 'verifying':
        setStatus(event.message)
        setStage('verifying')
        setProgress({ current: event.current, total: event.total })
        break

      case 'claim_result':
        setProgress({ current: event.current, total: event.total })
        // Update the specific claim with its result
        setClaims(prev =>
          prev.map(c => c.id === event.claim.id ? event.claim : c)
        )
        break

      case 'done':
        setStatus(event.message)
        setStage('done')
        setSummary(event.summary)
        setPhase(PHASE.DONE)
        break

      case 'error':
        setError(event.message)
        setPhase(PHASE.ERROR)
        break

      default:
        break
    }
  }, [])

  const handleReset = useCallback(() => {
    setFile(null)
    setPhase(PHASE.IDLE)
    setClaims([])
    setSummary(null)
    setError('')
    setStatus('')
    setProgress({ current: 0, total: 0 })
  }, [])

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-inner">
            <a href="/" className="logo">
              <div className="logo-icon">🔍</div>
              <span className="logo-text">TruthLayer</span>
            </a>
            <span className="header-badge">AI Fact-Checking Engine</span>
          </div>
        </div>
      </header>

      <main>
        <div className="container">
          {/* Hero */}
          <section className="hero">
            <div className="hero-tag">
              <span className="hero-tag-dot" />
              Powered by Gemini + Tavily Search
            </div>
            <h1>Stop Trusting.<br />Start Verifying.</h1>
            <p className="hero-subtitle">
              Upload any PDF and our AI agent extracts every factual claim,
              cross-references it against live web data, and flags what's
              real, outdated, or simply false.
            </p>
          </section>

          {/* Upload — shown when idle or after reset */}
          {(phase === PHASE.IDLE || phase === PHASE.ERROR) && (
            <>
              <UploadZone
                file={file}
                onFileSelect={handleFileSelect}
                onAnalyze={handleAnalyze}
                isLoading={phase === PHASE.LOADING}
              />
              {phase === PHASE.ERROR && (
                <div className="state-card" style={{ marginTop: 24 }}>
                  <span className="state-icon">⚠️</span>
                  <h3 className="state-title">Analysis Failed</h3>
                  <p className="state-desc">{error}</p>
                  <button className="reset-btn" onClick={handleReset}>
                    ↺ Try Again
                  </button>
                </div>
              )}
            </>
          )}

          {/* Loading — show upload zone + progress + live claims */}
          {phase === PHASE.LOADING && (
            <>
              <UploadZone
                file={file}
                onFileSelect={handleFileSelect}
                onAnalyze={handleAnalyze}
                isLoading={true}
              />
              <ProgressBar
                current={progress.current}
                total={progress.total}
                status={status}
                stage={stage}
              />
              {claims.length > 0 && (
                <div className="results-section">
                  <div className="results-header">
                    <h2 className="results-title">
                      Live Results — {claims.filter(c => c.verdict).length}/{claims.length} verified
                    </h2>
                  </div>
                  <div className="claims-list">
                    {claims.map((claim, index) => (
                      <ClaimCard key={claim.id} claim={claim} index={index} />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Done */}
          {phase === PHASE.DONE && claims.length > 0 && (
            <ResultsPanel
              claims={claims}
              summary={summary}
              onReset={handleReset}
            />
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>
            <strong>TruthLayer</strong> — Built for Cog Culture Assessment ·{' '}
            Powered by Google Gemini &amp; Tavily Search
          </p>
        </div>
      </footer>
    </div>
  )
}
