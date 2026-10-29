import React from 'react'
import { NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ShieldAlert, LayoutDashboard, Search, Building2, LogOut, LogIn, User, ShieldCheck } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        <div className="brand-icon">
          <ShieldAlert size={22} color="#ffffff" />
        </div>
        <div className="brand-text">
          <h1>GST Fraud Intel</h1>
          <p>Graph AI Platform</p>
        </div>
      </Link>

      {/* Role-based navigation links only shown when logged in */}
      {user && (
        <div className="nav-links">
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={17} />
            <span>Dashboard</span>
          </NavLink>

          {user.role === 'auditor' && (
            <NavLink to="/auditor" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Search size={17} />
              <span>Tax Auditor Portal</span>
            </NavLink>
          )}

          {user.role === 'supplier' && (
            <NavLink to="/msme" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Building2 size={17} />
              <span>MSME Supplier Risk</span>
            </NavLink>
          )}
        </div>
      )}

      {/* User Profile & Auth Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        {user ? (
          <>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: user.role === 'auditor' ? 'rgba(99,102,241,0.12)' : 'rgba(16,185,129,0.12)',
              border: `1px solid ${user.role === 'auditor' ? 'rgba(99,102,241,0.3)' : 'rgba(16,185,129,0.3)'}`,
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.78rem',
              color: user.role === 'auditor' ? '#a5b4fc' : '#34d399'
            }}>
              <User size={13} />
              <span style={{ fontWeight: 600 }}>{user.email}</span>
              <span style={{
                background: 'rgba(255,255,255,0.1)',
                padding: '0.15rem 0.45rem',
                borderRadius: '10px',
                fontSize: '0.68rem',
                textTransform: 'uppercase',
                fontWeight: 700,
                letterSpacing: '0.04em'
              }}>
                {user.role === 'auditor' ? 'Auditor' : 'MSME'}
              </span>
            </div>

            <button
              onClick={handleLogout}
              title="Sign Out"
              style={{
                background: 'rgba(239,68,68,0.1)',
                border: '1px solid rgba(239,68,68,0.3)',
                color: '#f87171',
                padding: '0.4rem 0.75rem',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                transition: 'all 0.2s'
              }}
            >
              <LogOut size={14} />
              <span>Logout</span>
            </button>
          </>
        ) : null}
      </div>
    </nav>
  )
}
