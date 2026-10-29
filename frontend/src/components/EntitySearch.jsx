import React, { useState, useEffect, useRef } from 'react'
import { Search, ArrowRight, History, X, Clock, Trash2 } from 'lucide-react'

const HISTORY_KEY = 'gst_searched_ids_history'

export default function EntitySearch({ onSearch, placeholder = "Enter 15-digit GSTIN (e.g. 27ABCDE1234F1Z5)..." }) {
  const [gstin, setGstin] = useState('')
  const [history, setHistory] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const containerRef = useRef(null)

  // Load search history from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(HISTORY_KEY)
      if (saved) {
        setHistory(JSON.parse(saved))
      }
    } catch {
      // Ignore
    }
  }, [])

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const saveToHistory = (id) => {
    const cleaned = id.trim().toUpperCase()
    if (!cleaned) return
    try {
      const updated = [cleaned, ...history.filter(item => item !== cleaned)].slice(0, 10)
      setHistory(updated)
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated))
    } catch {
      // Ignore
    }
  }

  const handleSelectHistory = (id) => {
    setGstin(id)
    setShowDropdown(false)
    saveToHistory(id)
    onSearch(id)
  }

  const handleRemoveHistoryItem = (e, id) => {
    e.stopPropagation()
    const updated = history.filter(item => item !== id)
    setHistory(updated)
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated))
    } catch {
      // Ignore
    }
  }

  const handleClearAllHistory = (e) => {
    e.stopPropagation()
    setHistory([])
    try {
      localStorage.removeItem(HISTORY_KEY)
    } catch {
      // Ignore
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const cleaned = gstin.trim().toUpperCase()
    if (cleaned) {
      saveToHistory(cleaned)
      setShowDropdown(false)
      onSearch(cleaned)
    }
  }

  return (
    <div ref={containerRef} style={{ position: 'relative', width: '100%', marginBottom: '2rem' }}>
      <form onSubmit={handleSubmit} className="search-box" style={{ marginBottom: 0 }}>
        <Search size={20} color="#94a3b8" />
        <input
          type="text"
          value={gstin}
          onFocus={() => setShowDropdown(true)}
          onClick={() => setShowDropdown(true)}
          onChange={(e) => setGstin(e.target.value.toUpperCase())}
          placeholder={placeholder}
          maxLength={15}
          autoComplete="off"
        />
        {gstin && (
          <button
            type="button"
            onClick={() => setGstin('')}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              padding: '0 4px',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Clear text"
          >
            <X size={16} />
          </button>
        )}
        <button type="submit" className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span>Inspect</span>
          <ArrowRight size={16} />
        </button>
      </form>

      {/* History Dropdown when input is focused/clicked */}
      {showDropdown && history.length > 0 && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 6px)',
          left: 0,
          right: 0,
          background: 'rgba(15, 22, 35, 0.98)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '12px',
          boxShadow: '0 12px 32px rgba(0, 0, 0, 0.6)',
          backdropFilter: 'blur(20px)',
          zIndex: 50,
          overflow: 'hidden'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.65rem 1rem',
            borderBottom: '1px solid var(--border-glass)',
            fontSize: '0.75rem',
            color: 'var(--text-dim)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#a5b4fc', fontWeight: 600 }}>
              <History size={14} />
              <span>Recent Searched GST IDs</span>
            </div>
            <button
              type="button"
              onClick={handleClearAllHistory}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-dim)',
                cursor: 'pointer',
                fontSize: '0.72rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem',
                transition: 'color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-dim)'}
            >
              <Trash2 size={12} />
              <span>Clear History</span>
            </button>
          </div>

          <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
            {history.map((id) => (
              <div
                key={id}
                onClick={() => handleSelectHistory(id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.65rem 1rem',
                  cursor: 'pointer',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.03)',
                  transition: 'background 0.15s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Clock size={14} color="#6366f1" />
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.88rem', fontWeight: 600, color: '#f1f5f9' }}>
                    {id}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={(e) => handleRemoveHistoryItem(e, id)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-dim)',
                    cursor: 'pointer',
                    padding: '2px 6px',
                    borderRadius: '4px'
                  }}
                  title="Remove from history"
                  onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-dim)'}
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick History Chips */}
      {history.length > 0 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.5rem',
          marginTop: '0.6rem',
          fontSize: '0.75rem'
        }}>
          <span style={{ color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.3rem', fontWeight: 600 }}>
            <History size={12} color="#a5b4fc" />
            Recent:
          </span>
          {history.slice(0, 4).map((id) => (
            <button
              key={id}
              type="button"
              onClick={() => handleSelectHistory(id)}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-glass)',
                borderRadius: '6px',
                padding: '0.2rem 0.55rem',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.72rem',
                color: '#a5b4fc',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(99, 102, 241, 0.15)'
                e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)'
                e.currentTarget.style.borderColor = 'var(--border-glass)'
              }}
            >
              {id}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
