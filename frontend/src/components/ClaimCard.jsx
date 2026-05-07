import React, { useCallback } from 'react'

const VERDICT_ICONS = {
  Verified: '✅',
  Inaccurate: '⚠️',
  False: '❌',
  Unverifiable: '❓',
}

const CONFIDENCE_COLORS = {
  Verified: '#10b981',
  Inaccurate: '#f59e0b',
  False: '#ef4444',
  Unverifiable: '#6b7280',
}

function getDomain(url) {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url.substring(0, 30)
  }
}

export default function ClaimCard({ claim, index }) {
  const isLoading = !claim.verdict

  const confidenceColor = CONFIDENCE_COLORS[claim.verdict] || '#6b7280'

  return (
    <div
      className={`claim-card ${claim.verdict || 'loading'}`}
      style={{ animationDelay: `${index * 0.05}s` }}
      id={`claim-${claim.id}`}
    >
      <div className="claim-header">
        <p className="claim-text">"{claim.claim}"</p>
        <div className="claim-meta">
          {claim.category && (
            <span className="category-badge">{claim.category}</span>
          )}
          {!isLoading && claim.verdict && (
            <span className={`verdict-badge ${claim.verdict}`}>
              {VERDICT_ICONS[claim.verdict]} {claim.verdict}
            </span>
          )}
          {isLoading && (
            <span className="verdict-badge Unverifiable">
              <span className="spinner" style={{ width: 10, height: 10, borderWidth: 1.5 }} />
              Checking...
            </span>
          )}
        </div>
      </div>

      {!isLoading && (
        <div className="claim-body">
          {/* Explanation */}
          {claim.explanation && (
            <p className="claim-explanation">{claim.explanation}</p>
          )}

          {/* Correction for Inaccurate/False */}
          {claim.correction && (
            <div className="claim-correction">
              <div className="correction-label">✏️ Correction</div>
              {claim.correction}
            </div>
          )}

          {/* Confidence bar */}
          {claim.confidence !== undefined && (
            <div className="confidence-bar">
              <span className="confidence-label">Confidence</span>
              <div className="confidence-track">
                <div
                  className="confidence-fill"
                  style={{
                    width: `${Math.round(claim.confidence * 100)}%`,
                    background: confidenceColor,
                  }}
                />
              </div>
              <span className="confidence-value">
                {Math.round(claim.confidence * 100)}%
              </span>
            </div>
          )}

          {/* Sources */}
          {claim.sources && claim.sources.length > 0 && (
            <div className="claim-sources">
              <span className="sources-label">Sources:</span>
              {claim.sources.slice(0, 3).map((url, i) => (
                <a
                  key={i}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link"
                  title={url}
                >
                  {getDomain(url)}
                </a>
              ))}
            </div>
          )}
        </div>
      )}

      {isLoading && (
        <div className="claim-loading-indicator">
          <span className="spinner" />
          Searching live web & verifying...
        </div>
      )}
    </div>
  )
}
