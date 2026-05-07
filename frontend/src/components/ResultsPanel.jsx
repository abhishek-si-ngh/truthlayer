import React, { useState } from 'react'
import ClaimCard from './ClaimCard'

const FILTERS = ['All', 'Verified', 'Inaccurate', 'False', 'Unverifiable']

export default function ResultsPanel({ claims, summary, onReset }) {
  const [activeFilter, setActiveFilter] = useState('All')

  const filtered = activeFilter === 'All'
    ? claims
    : claims.filter(c => c.verdict === activeFilter)

  const total = claims.length
  const verified = claims.filter(c => c.verdict === 'Verified').length
  const inaccurate = claims.filter(c => c.verdict === 'Inaccurate').length
  const falseCount = claims.filter(c => c.verdict === 'False').length
  const unverifiable = claims.filter(c => c.verdict === 'Unverifiable').length

  return (
    <div className="results-section">
      {/* Stats bar */}
      <div className="stats-bar" id="stats-summary">
        <div className="stat-card stat-verified">
          <div className="stat-number">{verified}</div>
          <div className="stat-label">✅ Verified</div>
        </div>
        <div className="stat-card stat-inaccurate">
          <div className="stat-number">{inaccurate}</div>
          <div className="stat-label">⚠️ Inaccurate</div>
        </div>
        <div className="stat-card stat-false">
          <div className="stat-number">{falseCount}</div>
          <div className="stat-label">❌ False</div>
        </div>
        <div className="stat-card stat-unverifiable">
          <div className="stat-number">{unverifiable}</div>
          <div className="stat-label">❓ Unverifiable</div>
        </div>
      </div>

      {/* Results header */}
      <div className="results-header">
        <h2 className="results-title">
          {total} Claims Analyzed
        </h2>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <div className="filter-tabs" id="filter-tabs">
            {FILTERS.map(f => (
              <button
                key={f}
                className={`filter-tab ${activeFilter === f ? 'active' : ''}`}
                onClick={() => setActiveFilter(f)}
                id={`filter-${f.toLowerCase()}`}
              >
                {f}
              </button>
            ))}
          </div>
          <button className="reset-btn" onClick={onReset} id="reset-btn">
            ↺ New PDF
          </button>
        </div>
      </div>

      {/* Claims list */}
      <div className="claims-list">
        {filtered.length === 0 ? (
          <div className="state-card">
            <span className="state-icon">🔍</span>
            <h3 className="state-title">No claims match this filter</h3>
            <p className="state-desc">Try selecting a different filter above.</p>
          </div>
        ) : (
          filtered.map((claim, index) => (
            <ClaimCard key={claim.id} claim={claim} index={index} />
          ))
        )}
      </div>
    </div>
  )
}
