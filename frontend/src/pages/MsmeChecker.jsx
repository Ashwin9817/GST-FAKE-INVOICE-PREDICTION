import React, { useState } from 'react'
import EntitySearch from '../components/EntitySearch'
import {
  ShieldCheck, ShieldAlert, AlertCircle,
  CheckCircle2, XCircle, Info, Loader2,
  AlertTriangle, TrendingUp, Shield
} from 'lucide-react'

const API_BASE = 'http://localhost:8000'

export default function MsmeChecker() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSearch = async (gstin) => {
    if (!gstin?.trim()) return
    setError(null); setResult(null); setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/risk-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ supplier_gstin: gstin.trim().toUpperCase() })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Verification failed')
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const riskCat = result?.risk_category || 'LOW'
  const riskColor = riskCat === 'HIGH' ? '#ef4444' : riskCat === 'MEDIUM' ? '#f59e0b' : '#10b981'
  const riskScore = result?.risk_score ?? 0
  const pct = Math.min(100, Math.max(0, riskScore))

  return (
    <div className="container">
      <div className="hero" style={{ marginBottom: '2rem' }}>
        <h2>MSME Supplier Risk Verification</h2>
        <p>
          Check if a supplier's GSTIN shows anomaly signals before issuing purchase orders or claiming Input Tax Credit (ITC).
          Powered by live network risk propagation scores.
        </p>
      </div>

      <EntitySearch onSearch={handleSearch} placeholder="Enter Supplier GSTIN (e.g. 27ABCDE1234F1Z5)..." />

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <Loader2 size={32} color="#6366f1" style={{ animation: 'spin 0.8s linear infinite', marginBottom: '0.75rem' }} />
          <p>Querying fraud risk engine...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '1rem 1.25rem', color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Result */}
      {result && !loading && (
        <div style={{ maxWidth: 640 }}>
          <div className="card" style={{ borderLeft: `4px solid ${riskColor}` }}>

            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem' }}>SUPPLIER GSTIN</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.1rem', fontWeight: 700, color: '#a5b4fc', marginBottom: '0.4rem' }}>{result.supplier_gstin}</div>
                {result.status === 'NOT_FOUND' && (
                  <div style={{ fontSize: '0.8rem', color: '#f59e0b' }}>⚠ Not found in database — using default low-risk profile</div>
                )}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem' }}>
                {riskCat === 'HIGH'
                  ? <span className="badge-high" style={{ fontSize: '0.85rem', padding: '0.35rem 0.9rem' }}><ShieldAlert size={14} /> High Anomaly Risk</span>
                  : riskCat === 'MEDIUM'
                  ? <span className="badge-medium" style={{ fontSize: '0.85rem', padding: '0.35rem 0.9rem' }}><AlertTriangle size={14} /> Medium Risk</span>
                  : <span className="badge-low" style={{ fontSize: '0.85rem', padding: '0.35rem 0.9rem' }}><ShieldCheck size={14} /> Low Risk</span>
                }
              </div>
            </div>

            {/* Risk Progress Bar */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Anomaly Risk Score</span>
                <span style={{ color: riskColor, fontWeight: 700 }}>{pct.toFixed(1)} / 100</span>
              </div>
              <div style={{ height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${pct}%`, background: riskColor, borderRadius: '999px', transition: 'width 0.6s ease' }} />
              </div>
            </div>

            {/* Propagated Risk */}
            {result.propagated_network_risk > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '8px', padding: '0.6rem 0.875rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
                <TrendingUp size={15} color="#f59e0b" />
                <span style={{ color: 'var(--text-muted)' }}>
                  Network propagated risk (1–2 hop neighbours):&nbsp;
                  <strong style={{ color: '#f59e0b' }}>{result.propagated_network_risk?.toFixed(1)} / 100</strong>
                </span>
              </div>
            )}

            {/* Warnings */}
            {result.warnings?.length > 0 && (
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ef4444', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <AlertCircle size={13} /> Risk Factors Identified
                </div>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {result.warnings.map((w, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      <XCircle size={13} color="#ef4444" style={{ flexShrink: 0, marginTop: 3 }} />
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendation */}
            <div style={{ background: `${riskColor}10`, border: `1px solid ${riskColor}30`, borderRadius: '8px', padding: '0.875rem 1rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start' }}>
                <Info size={16} color={riskColor} style={{ flexShrink: 0, marginTop: 2 }} />
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.85rem', color: riskColor, marginBottom: '0.3rem' }}>Recommendation</div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 }}>{result.recommendation}</p>
                </div>
              </div>
            </div>

            {/* Safe Signals */}
            {(riskCat === 'LOW' || riskCat === 'MEDIUM') && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1rem' }}>
                {['GST Returns Filed', 'No Circular Loops Detected', 'Normal Invoice Volume', 'Clean Network Topology'].map((item, i) => (
                  <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', color: '#34d399', padding: '0.2rem 0.6rem', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 600 }}>
                    <CheckCircle2 size={11} /> {item}
                  </span>
                ))}
              </div>
            )}

            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', lineHeight: 1.5, borderTop: '1px solid var(--border-glass)', paddingTop: '0.75rem' }}>
              This result is an analytical risk indicator generated by a B.Tech AIML research system. It is not an official government GST verification or legal determination of fraud.
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-dim)' }}>
          <Shield size={48} color="rgba(16,185,129,0.3)" style={{ marginBottom: '1rem' }} />
          <p style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Enter a supplier GSTIN to check their AI-computed anomaly risk score</p>
          <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>Checks for circular trading, invoice splitting, and network-level risk propagation</p>
        </div>
      )}
    </div>
  )
}
