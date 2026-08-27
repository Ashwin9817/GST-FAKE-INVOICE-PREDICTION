import React from 'react'
import { NavLink, Link } from 'react-router-dom'
import { ShieldAlert, LayoutDashboard, Search, Building2, Activity } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        <div className="brand-icon">
          <ShieldAlert size={24} color="#ffffff" />
        </div>
        <div className="brand-text">
          <h1>GST Fraud Intel</h1>
          <p>Graph AI Platform</p>
        </div>
      </Link>

      <div className="nav-links">
        <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/auditor" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Search size={18} />
          <span>Tax Auditor Portal</span>
        </NavLink>
        <NavLink to="/msme" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Building2 size={18} />
          <span>MSME Supplier Risk</span>
        </NavLink>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16, 185, 129, 0.1)', padding: '0.4rem 0.8rem', borderRadius: '20px', border: '1px solid rgba(16, 185, 129, 0.3)', fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>
        <Activity size={14} className="animate-pulse" />
        <span>Graph Engine Active</span>
      </div>
    </nav>
  )
}
