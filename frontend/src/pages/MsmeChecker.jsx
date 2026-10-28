import React, { useState } from 'react'
import EntitySearch from '../components/EntitySearch'
import {
  ShieldCheck, ShieldAlert, AlertCircle,
  CheckCircle2, XCircle, Info, Loader2,
  AlertTriangle, TrendingUp, Shield, Settings, Activity
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')

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
      {/* Hero Section with Spinning Gear Engine Indicator */}
      <div className="hero" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.3)', padding: '0.35rem 0.9rem', borderRadius: '20px', fontSize: '0.78rem', color: '#a5b4fc', marginBottom: '1rem' }}>
          <Settings size={14} className="animate-spin-slow" />
          <span>Risk Engine Active &amp; Monitoring</span>
        </div>
        <h2>MSME Supplier Risk Verification</h2>
        <p>
          Check if a supplier's GSTIN shows anomaly signals before issuing purchase orders or claiming Input Tax Credit (ITC).
          Powered by live network risk propagation scores.
        </p>
      </div>

      <EntitySearch onSearch={handleSearch} placeholder="Enter Supplier GSTIN (e.g. 27ABCDE1234F1Z5)..." />

      {/* Loading */}
      {loading && (
        <div className="card animate-fade-in-up" style={{ textAlign: 'center', padding: '3.5rem 2rem', color: 'var(--text-muted)' }}>
          <Loader2 size={36} color="#6366f1" className="animate-spin-fast" style={{ marginBottom: '1rem' }} />
          <p style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>Querying fraud risk engine &amp; analyzing trade network...</p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '0.35rem' }}>Evaluating PageRank centrality, circular trading loops &amp; 2-hop propagation risk</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="animate-fade-in-up" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '12px', padding: '1.25rem', color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <AlertCircle size={20} />
          <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{error}</span>
        </div>
      )}

      {/* Full-Width Result Box */}
      {result && !loading && (
        <div className="animate-fade-in-up" style={{ width: '100%' }}>
          <div className="card" style={{ borderLeft: `5px solid ${riskColor}`, width: '100%', padding: '1.75rem' }}>

            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.35rem' }}>
                  SUPPLIER GSTIN INSPECION
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.3rem', fontWeight: 700, color: '#a5b4fc', marginBottom: '0.4rem', letterSpacing: '0.02em' }}>
                  {result.supplier_gstin}
                </div>
                {result.status === 'NOT_FOUND' && (
                  <div style={{ fontSize: '0.82rem', color: '#f59e0b', fontWeight: 500 }}>⚠ Not found in index — using default low-risk profile</div>
                )}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.35rem' }}>
                {riskCat === 'HIGH'
                  ? <span className="badge-high animate-pulse-glow" style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}><ShieldAlert size={15} /> High Anomaly Risk</span>
                  : riskCat === 'MEDIUM'
                  ? <span className="badge-medium" style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}><AlertTriangle size={15} /> Medium Risk</span>
                  : <span className="badge-low" style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}><ShieldCheck size={15} /> Low Risk</span>
                }
              </div>
            </div>

            {/* Animated Risk Progress Bar */}
            <div style={{ marginBottom: '1.5rem', background: 'rgba(0,0,0,0.2)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.6rem', fontSize: '0.85rem' }}>
                <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Calculated Anomaly Risk Score</span>
                <span style={{ color: riskColor, fontWeight: 800, fontFamily: 'var(--font-mono)', fontSize: '1.05rem' }}>
                  {pct.toFixed(1)} / 100
                </span>
              </div>

              {/* Progress Track */}
              <div style={{ height: '10px', background: 'rgba(255,255,255,0.06)', borderRadius: '999px', overflow: 'hidden', position: 'relative' }}>
                <div
                  className="risk-bar-fill-animated"
                  style={{
                    width: `${pct}%`,
                    background: `linear-gradient(90deg, ${riskColor}88, ${riskColor})`,
                    boxShadow: `0 0 12px ${riskColor}aa`
                  }}
                />
              </div>
            </div>

            {/* Propagated Risk Indicator */}
            {result.propagated_network_risk > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: '10px', padding: '0.75rem 1rem', marginBottom: '1.25rem', fontSize: '0.9rem' }}>
                <TrendingUp size={18} color="#f59e0b" flexShrink={0} />
                <span style={{ color: 'var(--text-muted)' }}>
                  Network Propagated Risk (1–2 Hop Neighbors):&nbsp;
                  <strong style={{ color: '#f59e0b', fontFamily: 'var(--font-mono)', fontSize: '0.95rem' }}>
                    {result.propagated_network_risk?.toFixed(1)} / 100
                  </strong>
                </span>
              </div>
            )}

            {/* Warnings List */}
            {result.warnings?.length > 0 && (
              <div style={{ marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#ef4444', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.45rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  <AlertCircle size={15} /> Identified Anomaly Risk Factors
                </div>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {result.warnings.map((w, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem', fontSize: '0.88rem', color: 'var(--text-muted)', background: 'rgba(239,68,68,0.05)', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.15)' }}>
                      <XCircle size={15} color="#ef4444" style={{ flexShrink: 0, marginTop: 2 }} />
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendation Box */}
            <div style={{ background: `${riskColor}12`, border: `1px solid ${riskColor}35`, borderRadius: '12px', padding: '1rem 1.25rem', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <Info size={18} color={riskColor} style={{ flexShrink: 0, marginTop: 2 }} />
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem', color: riskColor, marginBottom: '0.35rem' }}>Recommended Action</div>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.6, margin: 0 }}>{result.recommendation}</p>
                </div>
              </div>
            </div>

            {/* Safe Signals */}
            {(riskCat === 'LOW' || riskCat === 'MEDIUM') && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
                {['GST Returns Filed', 'No Circular Loops Detected', 'Normal Invoice Volume', 'Clean Network Topology'].map((item, i) => (
                  <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: 5, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', color: '#34d399', padding: '0.3rem 0.75rem', borderRadius: '999px', fontSize: '0.78rem', fontWeight: 600 }}>
                    <CheckCircle2 size={13} /> {item}
                  </span>
                ))}
              </div>
            )}

            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.5, borderTop: '1px solid var(--border-glass)', paddingTop: '0.85rem', marginTop: '0.5rem' }}>
              ℹ This risk determination is generated by an unsupervised Isolation Forest &amp; Graph Neural Network intelligence pipeline.
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="card animate-fade-in-up" style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-dim)', width: '100%' }}>
          <Shield size={48} color="rgba(16,185,129,0.4)" style={{ marginBottom: '1rem' }} />
          <p style={{ fontSize: '1.05rem', color: 'var(--text-primary)', fontWeight: 600 }}>Enter a supplier GSTIN above to inspect risk status</p>
          <p style={{ fontSize: '0.85rem', marginTop: '0.4rem', color: 'var(--text-muted)' }}>Analyzes circular loops, invoice splitting &amp; network propagation score</p>
        </div>
      )}
    </div>
  )
}
