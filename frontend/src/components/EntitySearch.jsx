import React, { useState } from 'react'
import { Search, ArrowRight } from 'lucide-react'

export default function EntitySearch({ onSearch, placeholder = "Enter 15-digit GSTIN (e.g. 27ABCDE1234F1Z5)..." }) {
  const [gstin, setGstin] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (gstin.trim()) {
      onSearch(gstin.trim().toUpperCase())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="search-box">
      <Search size={20} color="#94a3b8" />
      <input
        type="text"
        value={gstin}
        onChange={(e) => setGstin(e.target.value.toUpperCase())}
        placeholder={placeholder}
        maxLength={15}
      />
      <button type="submit" className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
        <span>Inspect</span>
        <ArrowRight size={16} />
      </button>
    </form>
  )
}
