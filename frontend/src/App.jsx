import React from 'react'
import { Routes, Route, Navigate, useLocation, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import AuditorPortal from './pages/AuditorPortal'
import MsmeChecker from './pages/MsmeChecker'
import Login from './pages/Login'
import { ShieldAlert, Lock, ArrowRight, ShieldCheck, Search, Building2 } from 'lucide-react'

// Require Authentication Wrapper
function RequireAuth({ children }) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

// Require Specific Role Wrapper
function RequireRole({ allowedRole, children }) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (user.role !== allowedRole) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="card" style={{ maxWidth: '520px', padding: '2.5rem', textAlign: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '20px' }}>
          <div style={{ display: 'inline-flex', padding: '1rem', background: 'rgba(245,158,11,0.12)', borderRadius: '50%', marginBottom: '1.25rem' }}>
            <Lock size={36} color="#f59e0b" />
          </div>
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Portal Access Restricted
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
            You are logged in as <strong style={{ color: '#a5b4fc' }}>{user.name}</strong> ({user.email}). 
            This portal requires <strong style={{ color: '#f59e0b' }}>{allowedRole === 'auditor' ? 'Tax Auditor' : 'MSME Supplier'}</strong> clearance.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <Link
              to={user.role === 'auditor' ? '/auditor' : '/msme'}
              className="btn-primary"
              style={{ textDecoration: 'none' }}
            >
              <span>Go to {user.role === 'auditor' ? 'Auditor Portal' : 'MSME Checker'}</span>
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return children
}

function MainLayout() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={
          <RequireAuth>
            <Home />
          </RequireAuth>
        } />
        
        <Route path="/auditor" element={
          <RequireAuth>
            <RequireRole allowedRole="auditor">
              <AuditorPortal />
            </RequireRole>
          </RequireAuth>
        } />
        
        <Route path="/msme" element={
          <RequireAuth>
            <RequireRole allowedRole="supplier">
              <MsmeChecker />
            </RequireRole>
          </RequireAuth>
        } />

        {/* Catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <footer>
        <p>&copy; 2026 AI-Powered Graph-Based GST Fraud Detection &amp; Risk Intelligence Platform. B.Tech AIML Project.</p>
      </footer>
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  )
}
