import React from 'react'

export default function StatsCard({ title, value, subtext, icon: Icon, color }) {
  return (
    <div className="card" style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
      {Icon && (
        <div style={{ background: `${color}22`, padding: '0.6rem', borderRadius: '10px', flexShrink: 0 }}>
          <Icon size={22} color={color} />
        </div>
      )}
      <div>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>{title}</p>
        <p style={{ fontSize: '1.6rem', fontWeight: 700, fontFamily: 'var(--font-display)', letterSpacing: '-0.02em', lineHeight: 1 }}>{value}</p>
        {subtext && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{subtext}</p>}
      </div>
    </div>
  )
}
