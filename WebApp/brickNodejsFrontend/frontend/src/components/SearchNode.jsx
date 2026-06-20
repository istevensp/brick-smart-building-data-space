// src/components/SearchNode.jsx
import React, { useState, memo } from 'react'

export default memo(function SearchNode({ data }) {
  const [searchValue, setSearchValue] = useState('')
  const { isDarkMode, onSearch } = data

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && searchValue.trim()) {
      onSearch(searchValue.trim())
    }
  }

  const handleSearch = () => {
    if (searchValue.trim()) {
      onSearch(searchValue.trim())
    }
  }

  return (
    <div 
      className="search-node"
      style={{
        background: isDarkMode 
          ? 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)'
          : 'linear-gradient(135deg, #f0f0f0 0%, #ffffff 100%)',
        color: isDarkMode ? '#fff' : '#333',
        padding: '12px',
        borderRadius: '20px',
        minWidth: '250px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
        transition: 'all 0.3s ease',
        fontFamily: "'Fira Mono', monospace",
      }}
    >
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px',
        marginBottom: '8px'
      }}>
        <span style={{ fontSize: '20px' }}>🔍</span>
        <span style={{ fontSize: '14px', fontWeight: '600' }}>Buscar Sensor</span>
      </div>
      
      <div style={{ display: 'flex', gap: '4px' }}>
        <input
          type="text"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Nombre del sensor..."
          style={{
            flex: 1,
            padding: '6px 10px',
            borderRadius: '10px',
            border: `1px solid ${isDarkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'}`,
            background: isDarkMode ? 'rgba(0,0,0,0.3)' : 'rgba(255,255,255,0.8)',
            color: isDarkMode ? '#fff' : '#333',
            fontSize: '12px',
            fontFamily: "'Fira Mono', monospace",
            outline: 'none',
            transition: 'all 0.2s ease'
          }}
        />
        <button
          onClick={handleSearch}
          style={{
            padding: '6px 12px',
            borderRadius: '10px',
            border: 'none',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: '#fff',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            fontFamily: "'Fira Mono', monospace",
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'scale(1.05)'
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'scale(1)'
          }}
        >
          Buscar
        </button>
      </div>
    </div>
  )
})