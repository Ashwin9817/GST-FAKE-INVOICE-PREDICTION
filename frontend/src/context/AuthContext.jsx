import React, { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export const USERS = {
  auditor: {
    email: 'auditor@gmail.com',
    password: 'auditor',
    role: 'auditor',
    name: 'Senior Tax Auditor',
    portalName: 'Tax Auditor Forensic Portal',
    portalPath: '/auditor'
  },
  supplier: {
    email: 'supplier@gmail.com',
    password: 'supplier',
    role: 'supplier',
    name: 'MSME Supplier Admin',
    portalName: 'MSME Supplier Risk Shield',
    portalPath: '/msme'
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('gst_fraud_user')
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })

  const login = (email, password) => {
    const cleanEmail = email.trim().toLowerCase()
    const cleanPass = password.trim()

    if (cleanEmail === USERS.auditor.email && cleanPass === USERS.auditor.password) {
      const u = USERS.auditor
      setUser(u)
      localStorage.setItem('gst_fraud_user', JSON.stringify(u))
      return { success: true, user: u }
    }

    if (cleanEmail === USERS.supplier.email && cleanPass === USERS.supplier.password) {
      const u = USERS.supplier
      setUser(u)
      localStorage.setItem('gst_fraud_user', JSON.stringify(u))
      return { success: true, user: u }
    }

    return { success: false, message: 'Invalid credentials. Use auditor@gmail.com / auditor or supplier@gmail.com / supplier' }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('gst_fraud_user')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, USERS }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
