import React, { useState, useEffect } from 'react'
import EntitySearch from '../components/EntitySearch'
import {
  AlertCircle, Network, FileText, ShieldAlert,
  ArrowUpRight, ArrowDownLeft, Activity, Layers,
  RotateCcw, Loader2, ChevronRight, Info,
  TrendingUp, AlertTriangle, Shield, CheckCircle2, BarChart3
} from 'lucide-react'

const API_BASE = 'http://localhost:8000'

// ─── Risk Score Gauge ─────────────────────────────────────────────
function RiskGauge({ score }) {
  const color = score >= 70 ? '#ef4444' : score >= 40 ? '#f59e0b' : '#10b981'
  const pct = Math.min(100, Math.max(0, score))
  return (
    <div style={{ position: 'relative', display: 'inline-flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg width="100" height="56" viewBox="0 0 100 56">
        <path d="M10 50 A 40 40 0 0 1 90 50" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" strokeLinecap="round" />
        <path
          d="M10 50 A 40 40 0 0 1 90 50"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${(pct / 100) * 125.6} 125.6`}
        />
      </svg>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, color, marginTop: '-14px' }}>
        {score.toFixed(1)}
      </div>
      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>/ 100</div>
    </div>
  )
}

// ─── Alert Reason Card ────────────────────────────────────────────
function AlertReasonCard({ reason }) {
  const sevColors = { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#10b981' }
  const bg = { HIGH: 'rgba(239,68,68,0.08)', MEDIUM: 'rgba(245,158,11,0.08)', LOW: 'rgba(16,185,129,0.08)' }
  const col = sevColors[reason.severity] || '#6366f1'
  return (
    <div style={{
      background: bg[reason.severity] || 'rgba(99,102,241,0.08)',
      border: `1px solid ${col}33`,
      borderLeft: `3px solid ${col}`,
      borderRadius: '8px',
      padding: '0.75rem 1rem',
      marginBottom: '0.5rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
        <AlertTriangle size={14} color={col} />
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: col, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {reason.code}
        </span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginLeft: 'auto' }}>{reason.severity}</span>
      </div>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{reason.description}</p>
    </div>
  )
}

// ─── Network Graph ────────────────────────────────────────────────
function NetworkGraph({ center, nodes = [], edges = [] }) {
  const [hoveredNode, setHoveredNode] = useState(null)
  if (!nodes || !nodes.length) return null

  const W = 800, H = 460
  const cx = W / 2, cy = H / 2

  const centerNode = nodes.find(n => n.id === center) || { id: center, risk_category: 'HIGH' }

  const direct1HopSet = new Set()
  edges.forEach(e => {
    if (e.source === center) direct1HopSet.add(e.target)
    if (e.target === center) direct1HopSet.add(e.source)
  })

  const hop1Nodes = nodes.filter(n => n.id !== center && direct1HopSet.has(n.id)).slice(0, 24)
  const hop1Set = new Set(hop1Nodes.map(n => n.id))
  const hop2Nodes = nodes.filter(n => n.id !== center && !hop1Set.has(n.id)).slice(0, 32)

  const positions = {}
  positions[center] = { x: cx, y: cy, hop: 0 }

  const r1 = 135
  hop1Nodes.forEach((n, i) => {
    const angle = (i / Math.max(hop1Nodes.length, 1)) * 2 * Math.PI - Math.PI / 2
    positions[n.id] = { x: cx + r1 * Math.cos(angle), y: cy + r1 * Math.sin(angle), hop: 1 }
  })

  const r2 = 205
  hop2Nodes.forEach((n, i) => {
    const angle = (i / Math.max(hop2Nodes.length, 1)) * 2 * Math.PI - Math.PI / 2
    positions[n.id] = { x: cx + r2 * Math.cos(angle), y: cy + r2 * Math.sin(angle), hop: 2 }
  })

  const renderedNodes = [centerNode, ...hop1Nodes, ...hop2Nodes]
  const renderedIdSet = new Set(renderedNodes.map(n => n.id))
  const validEdges = edges.filter(e => renderedIdSet.has(e.source) && renderedIdSet.has(e.target)).slice(0, 80)

  return (
    <div style={{ position: 'relative', width: '100%', background: 'rgba(255,255,255,0.02)', borderRadius: '14px', border: '1px solid var(--border-glass)', overflow: 'hidden' }}>
      {/* Legend */}
      <div style={{ padding: '0.6rem 1rem', background: 'rgba(0,0,0,0.2)', borderBottom: '1px solid var(--border-glass)', display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        <span style={{ fontWeight: 700, color: 'var(--text-dim)' }}>Legend:</span>
        <span>🟣 Target Entity</span>
        <span>🔵 1-Hop Partner (direct trade)</span>
        <span>⚫ 2-Hop Extended Network</span>
        <span>🔴 High-Risk Node</span>
        <span>─── Fraud Edge</span>
        <span style={{ opacity: 0.6 }}>─── Normal Edge</span>
      </div>

      <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`}>
        {/* Guide rings */}
        <circle cx={cx} cy={cy} r={r1} fill="none" stroke="rgba(99,102,241,0.15)" strokeDasharray="4 4" strokeWidth="1" />
        <circle cx={cx} cy={cy} r={r2} fill="none" stroke="rgba(255,255,255,0.06)" strokeDasharray="3 6" strokeWidth="1" />
        <text x={cx + 5} y={cy - r1 - 6} fill="rgba(99,102,241,0.5)" fontSize="9" fontFamily="Inter, sans-serif">1-HOP TRADE BOUNDARY</text>
        <text x={cx + 5} y={cy - r2 - 6} fill="rgba(255,255,255,0.2)" fontSize="9" fontFamily="Inter, sans-serif">2-HOP EXTENDED NETWORK</text>

        {/* Edges */}
        {validEdges.map((e, i) => {
          const s = positions[e.source], t = positions[e.target]
          if (!s || !t) return null
          const isFraud = e.fraud_pattern && e.fraud_pattern !== 'NONE' && e.fraud_pattern !== 'nan'
          const toCenter = e.source === center || e.target === center
          return (
            <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y}
              stroke={isFraud ? '#ef4444' : toCenter ? '#6366f1' : 'rgba(255,255,255,0.12)'}
              strokeWidth={isFraud ? 2 : toCenter ? 1.5 : 0.8}
              strokeOpacity={isFraud ? 0.9 : toCenter ? 0.7 : 0.5}
            />
          )
        })}

        {/* Nodes */}
        {renderedNodes.map(n => {
          const p = positions[n.id]
          if (!p) return null
          const isCenter = n.id === center
          const isHop1 = p.hop === 1
          const rCat = n.risk_category || 'LOW'
          const isHigh = rCat === 'HIGH'
          const isMed = rCat === 'MEDIUM'
          const r = isCenter ? 18 : isHop1 ? 9 : 6
          const fill = isCenter ? '#6366f1' : isHigh ? '#ef4444' : isMed ? '#f59e0b' : isHop1 ? '#3b82f6' : 'rgba(148,163,184,0.6)'

          return (
            <g key={n.id} style={{ cursor: 'pointer' }}
              onMouseEnter={() => setHoveredNode(n)}
              onMouseLeave={() => setHoveredNode(null)}>
              <circle cx={p.x} cy={p.y} r={r + (isCenter ? 4 : 2)} fill={fill} opacity="0.15" />
              <circle cx={p.x} cy={p.y} r={r} fill={fill} stroke="rgba(255,255,255,0.2)" strokeWidth={isCenter ? 2 : 1} />
              {(isCenter || isHop1 || isHigh) && (
                <text x={p.x} y={p.y + r + 12} textAnchor="middle"
                  fill={isCenter ? '#a5b4fc' : isHigh ? '#f87171' : 'rgba(148,163,184,0.8)'}
                  fontSize={isCenter ? '10' : '8'}
                  fontWeight={isCenter ? '700' : '400'}
                  fontFamily="JetBrains Mono, monospace"
                >{n.id.slice(0, 8)}</text>
              )}
            </g>
          )
        })}
      </svg>

      {/* Tooltip */}
      {hoveredNode && (
        <div style={{
          position: 'absolute', bottom: 12, left: 12,
          background: 'rgba(15,22,36,0.95)',
          border: '1px solid var(--border-glass)',
          borderRadius: '10px',
          padding: '0.75rem 1rem',
          backdropFilter: 'blur(12px)',
          fontSize: '0.8rem',
          pointerEvents: 'none',
          minWidth: 200
        }}>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginBottom: 4 }}>ENTITY NODE</div>
          <div style={{ fontFamily: 'var(--font-mono)', color: '#a5b4fc', fontWeight: 700, marginBottom: 6 }}>{hoveredNode.id}</div>
          <div style={{ display: 'flex', gap: 6 }}>
            <span className={`badge-${(hoveredNode.risk_category || 'LOW').toLowerCase()}`}>
              {hoveredNode.risk_category || 'LOW'}
            </span>
            {hoveredNode.risk_score != null && (
              <span style={{ color: 'var(--text-dim)', fontSize: '0.72rem' }}>Score: {hoveredNode.risk_score?.toFixed(1)}/100</span>
            )}
          </div>
          {hoveredNode.id === center && (
            <div style={{ marginTop: 4, fontSize: '0.7rem', color: '#a5b4fc' }}>★ Target Entity</div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Main Auditor Portal ──────────────────────────────────────────
export default function AuditorPortal() {
  const [gstin, setGstin] = useState('')
  const [profile, setProfile] = useState(null)
  const [txs, setTxs] = useState([])
  const [network, setNetwork] = useState(null)
  const [alert, setAlert] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/stats`).then(r => r.json()).then(setStats).catch(() => null)
  }, [])

  const handleSearch = async (searchGstin) => {
    if (!searchGstin?.trim()) return
    setGstin(searchGstin)
    setError(null)
    setLoading(true)
    setProfile(null); setTxs([]); setNetwork(null); setAlert(null)

    try {
      const [profRes, txRes, netRes, alertRes] = await Promise.all([
        fetch(`${API_BASE}/api/entities/${searchGstin}`),
        fetch(`${API_BASE}/api/entities/${searchGstin}/transactions?limit=10`),
        fetch(`${API_BASE}/api/entities/${searchGstin}/network?hops=2`),
        fetch(`${API_BASE}/api/entities/${searchGstin}/alert`)
      ])
      if (!profRes.ok) throw new Error(`GSTIN "${searchGstin}" not found in database`)
      const [profData, txData, netData, alertData] = await Promise.all([
        profRes.json(), txRes.json(), netRes.json(), alertRes.json()
      ])
      setProfile(profData); setTxs(Array.isArray(txData) ? txData : [])
      setNetwork(netData); setAlert(alertData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const risk = profile?.risk || {}
  const entity = profile?.entity || {}
  const features = profile?.features || {}
  const riskScore = risk.final_risk_score ?? risk.risk_score ?? 0
  const riskCat = risk.risk_category || 'LOW'
  const riskColor = riskCat === 'HIGH' ? '#ef4444' : riskCat === 'MEDIUM' ? '#f59e0b' : '#10b981'
  const badgeClass = riskCat === 'HIGH' ? 'badge-high' : riskCat === 'MEDIUM' ? 'badge-medium' : 'badge-low'

  return (
    <div className="container">
      <div className="hero" style={{ marginBottom: '2rem' }}>
        <h2>Tax Auditor Forensic Portal</h2>
        <p>Inspect entity risk scores, 1–2 hop transaction graphs, loop closures, and explainable AI fraud alerts.</p>
      </div>

      {/* Platform Stats Strip */}
      {stats && (
        <div className="grid-stats" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', marginBottom: '1.5rem' }}>
          {[
            { label: 'Total Entities', value: stats.total_entities?.toLocaleString(), icon: BarChart3, color: '#6366f1' },
            { label: 'Total Invoices', value: stats.total_transactions?.toLocaleString(), icon: FileText, color: '#06b6d4' },
            { label: 'High Risk', value: stats.high_risk_count, icon: ShieldAlert, color: '#ef4444' },
            { label: 'Medium Risk', value: stats.medium_risk_count, icon: AlertTriangle, color: '#f59e0b' },
            { label: 'Low Risk', value: stats.low_risk_count, icon: CheckCircle2, color: '#10b981' },
            { label: 'Avg Risk Score', value: stats.average_risk_score, icon: TrendingUp, color: '#a855f7' },
          ].map((s, i) => {
            const Icon = s.icon
            return (
              <div key={i} className="card" style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', padding: '0.9rem 1rem' }}>
                <div style={{ background: `${s.color}22`, padding: '0.4rem', borderRadius: '7px', flexShrink: 0 }}>
                  <Icon size={16} color={s.color} />
                </div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{s.label}</p>
                  <p style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-display)', color: s.color }}>{s.value}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <EntitySearch onSearch={handleSearch} />

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <Loader2 size={32} color="#6366f1" style={{ animation: 'spin 0.8s linear infinite', marginBottom: '0.75rem' }} />
          <p>Querying risk engine...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '1rem 1.25rem', color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {profile && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {/* Entity Risk Header Card */}
          <div className="card" style={{ borderLeft: `4px solid ${riskColor}` }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
              <div style={{ flex: 1, minWidth: 220 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '1.1rem', fontWeight: 700, color: '#a5b4fc' }}>{entity.gstin}</span>
                  <span className={badgeClass}>{riskCat} RISK</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                  {entity.state} · {entity.category}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{entity.business_size}</div>
              </div>
              <RiskGauge score={riskScore} />
              {risk.propagated_network_risk > 0 && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Network Propagated</div>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', fontWeight: 800, color: '#f59e0b' }}>
                    {risk.propagated_network_risk?.toFixed(1)}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>/ 100</div>
                </div>
              )}
              {risk.anomaly_rank && (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Anomaly Rank</div>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {risk.anomaly_rank}
                  </div>
                </div>
              )}
            </div>

            {/* Topology Features Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem' }}>
              {[
                { label: 'PageRank Centrality', value: features.pagerank != null ? Number(features.pagerank).toFixed(4) : '—' },
                { label: 'Louvain Community', value: features.community_id != null ? `COMM_${String(features.community_id).slice(0,4)}` : '—' },
                { label: 'Circular Loop', value: features.has_loop ? `${features.shortest_loop_dist}-Hop Detected` : 'None Detected' },
                { label: 'Out-Degree (Sales)', value: features.out_degree ?? '—' },
                { label: 'In-Degree (Purchases)', value: features.in_degree ?? '—' },
                { label: 'Tx Velocity / Day', value: features.tx_per_day != null ? Number(features.tx_per_day).toFixed(1) : '—' },
                { label: '24h Burst Max', value: features.burst_24h_max != null ? `${features.burst_24h_max} invoices` : '—' },
                { label: 'Total Turnover', value: features.total_turnover != null ? `₹${Number(features.total_turnover).toLocaleString('en-IN', { maximumFractionDigits: 0 })}` : '—' },
              ].map((f, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', borderRadius: '8px', padding: '0.65rem 0.75rem' }}>
                  <div style={{ fontSize: '0.67rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem' }}>{f.label}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{String(f.value)}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Explainability Alert */}
          {alert && (
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
                <Info size={18} color="#6366f1" />
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 700 }}>Explainable Fraud Alert Analysis</h3>
              </div>
              <div style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: '8px', padding: '0.75rem 1rem', marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                <strong style={{ color: 'var(--text-primary)' }}>AI Summary: </strong>{alert.natural_language_summary}
              </div>
              {alert.reasons?.map((r, i) => <AlertReasonCard key={i} reason={r} />)}
              <div style={{ marginTop: '0.75rem', padding: '0.6rem 0.875rem', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                ⚠ Risk indicators are analytical outputs and do not constitute confirmation of GST fraud. High-risk entities require further investigation.
              </div>
            </div>
          )}

          {/* Network Graph */}
          {network && (
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Network size={18} color="#6366f1" />
                  <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 700 }}>1–2 Hop Transaction Network Graph</h3>
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', background: 'rgba(255,255,255,0.04)', padding: '0.2rem 0.6rem', borderRadius: '999px', border: '1px solid var(--border-glass)' }}>
                  {network.nodes?.length} nodes · {network.edges?.length} edges
                </span>
              </div>
              <NetworkGraph center={gstin} nodes={network.nodes} edges={network.edges} />
            </div>
          )}

          {/* Transaction Log */}
          {txs.length > 0 && (
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
                <FileText size={18} color="#06b6d4" />
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 700 }}>Recent Invoice Log</h3>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Invoice ID</th>
                      <th>Date</th>
                      <th>Direction</th>
                      <th>Counterparty GSTIN</th>
                      <th>Taxable Amount</th>
                      <th>Fraud Pattern</th>
                      <th>Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {txs.map((tx, i) => {
                      const isPatternFraud = tx.fraud_pattern && tx.fraud_pattern !== 'NONE' && tx.fraud_pattern !== 'nan'
                      const cCat = tx.counterparty_risk_category || 'LOW'
                      const isHigh = isPatternFraud || cCat === 'HIGH'
                      const isMed = !isHigh && cCat === 'MEDIUM'
                      const badgeClass = isHigh ? 'badge-high' : isMed ? 'badge-medium' : 'badge-low'
                      const badgeText = isPatternFraud
                        ? `HIGH (${tx.fraud_pattern})`
                        : cCat === 'HIGH' ? 'HIGH (COUNTERPARTY)'
                        : cCat === 'MEDIUM' ? 'MEDIUM (COUNTERPARTY)' : 'NORMAL'

                      return (
                        <tr key={i}>
                          <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#a5b4fc' }}>{tx.invoice_id}</span></td>
                          <td style={{ fontSize: '0.8rem' }}>{String(tx.invoice_date).slice(0, 16)}</td>
                          <td>
                            {tx.direction === 'OUTGOING'
                              ? <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: '#f87171' }}><ArrowUpRight size={14} />Sale</span>
                              : <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: '#34d399' }}><ArrowDownLeft size={14} />Purchase</span>
                            }
                          </td>
                          <td><span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{tx.direction === 'OUTGOING' ? tx.buyer_gstin : tx.seller_gstin}</span></td>
                          <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>₹{Number(tx.taxable_amount || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                          <td>
                            <span style={{ fontSize: '0.72rem', padding: '0.15rem 0.5rem', borderRadius: '5px', background: isPatternFraud ? 'rgba(239,68,68,0.12)' : 'rgba(255,255,255,0.04)', color: isPatternFraud ? '#f87171' : 'var(--text-dim)', border: `1px solid ${isPatternFraud ? 'rgba(239,68,68,0.3)' : 'var(--border-glass)'}` }}>
                              {isPatternFraud ? tx.fraud_pattern : 'STANDARD_TRADE'}
                            </span>
                          </td>
                          <td><span className={badgeClass}>{badgeText}</span></td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!profile && !loading && !error && (
        <div style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-dim)' }}>
          <Network size={48} color="rgba(99,102,241,0.3)" style={{ marginBottom: '1rem' }} />
          <p style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Enter a GSTIN above to query the AI fraud detection engine</p>
          <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>Explore risk scores, graph topology, and fraud alert explanations</p>
        </div>
      )}
    </div>
  )
}
