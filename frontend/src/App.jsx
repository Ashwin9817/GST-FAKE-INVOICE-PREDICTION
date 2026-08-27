import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import AuditorPortal from './pages/AuditorPortal'
import MsmeChecker from './pages/MsmeChecker'

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/auditor" element={<AuditorPortal />} />
        <Route path="/msme" element={<MsmeChecker />} />
      </Routes>
      <footer>
        <p>&copy; 2026 AI-Powered Graph-Based GST Fraud Detection &amp; Risk Intelligence Platform. B.Tech AIML Project.</p>
      </footer>
    </>
  )
}
