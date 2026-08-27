import React from 'react'
import { Link } from 'react-router-dom'
import { Users, FileText, AlertTriangle, Network, ShieldCheck, Zap, GitFork, RotateCcw } from 'lucide-react'
import StatsCard from '../components/StatsCard'

export default function Home() {
  return (
    <div className="container">
      {/* Hero Section */}
      <div className="hero">
        <div className="hero-badge">
          <Zap size={14} />
          <span>Graph Neural Network &amp; Isolation Forest Platform</span>
        </div>
        <h2>AI-Powered Graph GST Fraud Detection &amp; Risk Intelligence</h2>
        <p>
          Detecting circular trading, star-shaped collusion, split invoicing, and high-velocity fraud
          through multi-hop business transaction graph embeddings and hybrid feature fusion.
        </p>
      </div>

      {/* KPI Stats Row */}
      <div className="grid-stats">
        <StatsCard title="Tracked Entities" value="500" subtext="Active GSTIN Businesses" icon={Users} color="#6366f1" />
        <StatsCard title="Total Transactions" value="3,000" subtext="Directed Invoice Graph Edges" icon={FileText} color="#06b6d4" />
        <StatsCard title="Flagged Fraud Invoices" value="123" subtext="Ground Truth Synthetic Anomalies" icon={AlertTriangle} color="#ef4444" />
        <StatsCard title="Graph Topology" value="GraphSAGE" subtext="64-Dim Node Embeddings" icon={Network} color="#10b981" />
      </div>

      {/* Portal Entry Options */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '20px', padding: '2rem', backdropFilter: 'blur(16px)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ background: 'rgba(99, 102, 241, 0.2)', padding: '0.75rem', borderRadius: '12px' }}>
              <Network size={28} color="#6366f1" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-display)', fontWeight: 700 }}>Tax Auditor Portal</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Deep Forensic Investigation</p>
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
            Explore 1-2 hop transaction graphs, detect circular loop closures, analyze GraphSAGE node embeddings, and inspect explainable alert breakdowns.
          </p>
          <Link to="/auditor" className="btn-primary" style={{ display: 'inline-block', textDecoration: 'none' }}>
            Launch Auditor Portal &rarr;
          </Link>
        </div>

        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '20px', padding: '2rem', backdropFilter: 'blur(16px)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.2)', padding: '0.75rem', borderRadius: '12px' }}>
              <ShieldCheck size={28} color="#10b981" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-display)', fontWeight: 700 }}>MSME Supplier Checker</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Supplier Verification</p>
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
            Allows small business buyers to verify supplier GSTIN risk status before issuing purchase orders or claiming Input Tax Credits (ITC).
          </p>
          <Link to="/msme" className="btn-primary" style={{ display: 'inline-block', textDecoration: 'none', background: 'linear-gradient(135deg, #10b981, #059669)' }}>
            Check Supplier Risk &rarr;
          </Link>
        </div>
      </div>

      {/* Fraud Archetype Showcase */}
      <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '1.5rem' }}>Detected Fraud Archetypes</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '14px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', fontWeight: 700, marginBottom: '0.5rem' }}>
            <RotateCcw size={18} />
            <span>Circular Trading</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Closed-loop transaction chains (A &rarr; B &rarr; C &rarr; A) passing bogus invoices to inflate turnover and claim fraudulent ITC without actual movement of goods.
          </p>
        </div>

        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '14px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f59e0b', fontWeight: 700, marginBottom: '0.5rem' }}>
            <GitFork size={18} />
            <span>Star-Shaped Collusion</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Central shell aggregator hub transacting with multiple dummy suppliers or shell buyers to pass artificial invoice credits across networks.
          </p>
        </div>

        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '14px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#06b6d4', fontWeight: 700, marginBottom: '0.5rem' }}>
            <Zap size={18} />
            <span>Split Invoicing</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Splitting large commercial transactions into multiple sub-₹50,000 invoices (e.g. ₹49,200) within short windows to evade mandatory e-way bill generation.
          </p>
        </div>

        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-glass)', borderRadius: '14px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#a855f7', fontWeight: 700, marginBottom: '0.5rem' }}>
            <AlertTriangle size={18} />
            <span>High Velocity Burst</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Anomalous spike in transaction frequency over 24-48 hours from new or previously dormant entities before disappearing from statutory filings.
          </p>
        </div>
      </div>
    </div>
  )
}
