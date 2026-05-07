import React, { useCallback, useRef } from 'react'

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function UploadZone({ file, onFileSelect, onAnalyze, isLoading }) {
  const inputRef = useRef(null)

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    e.currentTarget.classList.add('drag-over')
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.currentTarget.classList.remove('drag-over')
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.currentTarget.classList.remove('drag-over')
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.type === 'application/pdf') {
      onFileSelect(dropped)
    } else {
      alert('Please drop a PDF file.')
    }
  }, [onFileSelect])

  const handleChange = useCallback((e) => {
    const selected = e.target.files[0]
    if (selected) onFileSelect(selected)
  }, [onFileSelect])

  return (
    <div className="upload-section">
      <div
        className="upload-zone"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !file && inputRef.current?.click()}
        id="upload-zone"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          onChange={handleChange}
          style={{ display: 'none' }}
          id="pdf-file-input"
        />

        {!file ? (
          <>
            <span className="upload-icon">📄</span>
            <h2 className="upload-title">Drop your PDF here</h2>
            <p className="upload-subtitle">
              or click to browse — we'll extract and verify every claim
            </p>
            <button className="upload-btn" type="button" onClick={(e) => {
              e.stopPropagation()
              inputRef.current?.click()
            }}>
              📂 Choose PDF
            </button>
            <p className="upload-note">Supports PDF up to 10MB</p>
          </>
        ) : (
          <>
            <span className="upload-icon">📋</span>
            <h2 className="upload-title">PDF Ready</h2>
            <p className="upload-subtitle">Click below to start fact-checking</p>
            <div className="file-selected" onClick={(e) => e.stopPropagation()}>
              <span style={{ fontSize: 28 }}>📄</span>
              <div className="file-info">
                <span className="file-name">{file.name}</span>
                <span className="file-size">{formatBytes(file.size)}</span>
              </div>
              <button
                className="reset-btn"
                onClick={(e) => { e.stopPropagation(); onFileSelect(null) }}
                type="button"
              >
                ✕ Remove
              </button>
            </div>
          </>
        )}
      </div>

      {file && (
        <button
          className="analyze-btn"
          onClick={onAnalyze}
          disabled={isLoading}
          id="analyze-btn"
          type="button"
        >
          {isLoading ? (
            <>
              <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
              Analyzing...
            </>
          ) : (
            <>🔍 Start Fact-Check</>
          )}
        </button>
      )}
    </div>
  )
}
