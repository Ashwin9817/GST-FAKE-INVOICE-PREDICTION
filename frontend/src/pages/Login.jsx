import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ShieldAlert, Search, Building2, Lock, Mail, Key, LogIn, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react'

export default function Login() {
  const { login, USERS } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const from = location.state?.from?.pathname

  const handleFormSubmit = (e) => {
    e.preventDefault()
    setError('')
    const res = login(email, password)
    if (res.success) {
      const targetPath = from || (res.user.role === 'auditor' ? '/auditor' : '/msme')
      navigate(targetPath, { replace: true })
    } else {
      setError(res.message)
    }
  }

  const handleQuickLogin = (roleKey) => {
    setError('')
    const preset = USERS[roleKey]
    setEmail(preset.email)
    setPassword(preset.password)
    const res = login(preset.email, preset.password)
    if (res.success) {
      const targetPath = from || (roleKey === 'auditor' ? '/auditor' : '/msme')
      navigate(targetPath, { replace: true })
    }
  }

  return (
    <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 'calc(100vh - 160px)', padding: '2rem 1rem' }}>
      
      {/* Brand Header */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.02em', background: 'linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          GST Fraud Intelligence Platform
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '0.35rem' }}>
          Dual-Portal Authentication System & Risk Analytics Engine
        </p>
      </div>

      {/* Main Login Card */}
      <div className="card" style={{ width: '100%', maxWidth: '480px', padding: '2.25rem', background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '20px', backdropFilter: 'blur(20px)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
          <Lock size={18} color="#6366f1" />
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', fontWeight: 700 }}>Portal Sign In</h3>
        </div>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '0.85rem 1rem', color: '#f87171', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <AlertCircle size={16} flexShrink={0} />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleFormSubmit}>
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Email Address
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-glass)', borderRadius: '10px', padding: '0 0.85rem' }}>
              <Mail size={16} color="var(--text-dim)" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="auditor@gmail.com or supplier@gmail.com"
                style={{ width: '100%', background: 'transparent', border: 'none', outline: 'none', color: 'var(--text-primary)', padding: '0.75rem 0', fontSize: '0.9rem', fontFamily: 'var(--font-mono)' }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '1.75rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Password
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-glass)', borderRadius: '10px', padding: '0 0.85rem' }}>
              <Key size={16} color="var(--text-dim)" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password..."
                style={{ width: '100%', background: 'transparent', border: 'none', outline: 'none', color: 'var(--text-primary)', padding: '0.75rem 0', fontSize: '0.9rem', fontFamily: 'var(--font-mono)' }}
              />
            </div>
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.75rem', fontSize: '0.95rem', borderRadius: '10px' }}>
            <LogIn size={18} />
            <span>Sign In to Portal</span>
          </button>
        </form>

        {/* Quick Demo Logins Divider */}
        <div style={{ display: 'flex', alignItems: 'center', margin: '1.75rem 0 1.25rem', gap: '1rem' }}>
          <div style={{ flex: 1, height: '1px', background: 'var(--border-glass)' }} />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            1-Click Demo Login Presets
          </span>
          <div style={{ flex: 1, height: '1px', background: 'var(--border-glass)' }} />
        </div>

        {/* Preset Buttons */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
          <button
            type="button"
            onClick={() => handleQuickLogin('auditor')}
            style={{
              background: 'rgba(99,102,241,0.12)',
              border: '1px solid rgba(99,102,241,0.3)',
              borderRadius: '10px',
              padding: '0.75rem 0.5rem',
              color: '#a5b4fc',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.2s'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontWeight: 700, fontSize: '0.85rem' }}>
              <Search size={14} color="#6366f1" />
              <span>Tax Auditor</span>
            </div>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>auditor@gmail.com</span>
          </button>

          <button
            type="button"
            onClick={() => handleQuickLogin('supplier')}
            style={{
              background: 'rgba(16,185,129,0.12)',
              border: '1px solid rgba(16,185,129,0.3)',
              borderRadius: '10px',
              padding: '0.75rem 0.5rem',
              color: '#34d399',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.2s'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontWeight: 700, fontSize: '0.85rem' }}>
              <Building2 size={14} color="#10b981" />
              <span>MSME Supplier</span>
            </div>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>supplier@gmail.com</span>
          </button>
        </div>

      </div>

      {/* Info Notice */}
      <div style={{ marginTop: '1.75rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-dim)', maxWidth: '420px', lineHeight: 1.5 }}>
        🔒 Role-Based Access Control: Tax Auditors access forensic network graphs; MSME Suppliers verify counterparty ITC risk.
      </div>
    </div>
  )
}
