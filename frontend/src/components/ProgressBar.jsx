import React from 'react'

export default function ProgressBar({ current, total, status, stage }) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0

  const stageLabels = {
    parsing: '📄 Parsing PDF',
    extracting: '🔍 Extracting Claims',
    verifying: `🔎 Verifying Claims (${current}/${total})`,
    done: '✅ Complete',
  }

  return (
    <div className="progress-section">
      <div className="progress-card">
        <div className="progress-header">
          <span className="progress-title">{stageLabels[stage] || 'Processing...'}</span>
          {total > 0 && stage === 'verifying' && (
            <span className="progress-step">{pct}%</span>
          )}
        </div>

        {stage === 'verifying' && (
          <div className="progress-bar-track">
            <div
              className="progress-bar-fill"
              style={{ width: `${pct}%` }}
            />
          </div>
        )}

        <div className="status-message">
          {stage !== 'done' && <span className="spinner" />}
          <span>{status}</span>
        </div>
      </div>
    </div>
  )
}
