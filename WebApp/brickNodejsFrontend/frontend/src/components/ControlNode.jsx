// src/components/ControlNode.jsx
import React, { memo } from 'react'

export default memo(function ControlNode({ data, selected }) {
  const { icon, label, isDarkMode, isActive, categoryColor } = data
  
  return (
    <div 
      className={`control-node ${isDarkMode ? 'dark' : 'light'} ${isActive ? 'active' : ''} ${selected ? 'selected' : ''}`}
      style={{
        background: isDarkMode 
          ? isActive 
            ? `linear-gradient(135deg, ${categoryColor || '#667eea'} 0%, ${categoryColor ? categoryColor + '99' : '#764ba2'} 100%)`
            : 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)'
          : isActive
            ? `linear-gradient(135deg, ${categoryColor || '#667eea'} 0%, ${categoryColor ? categoryColor + '99' : '#764ba2'} 100%)`
            : 'linear-gradient(135deg, #f0f0f0 0%, #ffffff 100%)',
        color: isDarkMode || isActive ? '#fff' : '#333',
        padding: '12px 20px',
        borderRadius: '20px',
        minWidth: '140px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        boxShadow: selected 
          ? '0 0 20px rgba(233, 42, 103, 0.5)'
          : isActive && categoryColor
            ? `0 4px 12px ${categoryColor}50`
            : '0 4px 6px rgba(0, 0, 0, 0.1)',
        border: `2px solid ${
          isActive && categoryColor
            ? categoryColor
            : isActive 
              ? '#8b5cf6'
              : isDarkMode 
                ? 'rgba(255,255,255,0.1)' 
                : 'rgba(0,0,0,0.1)'
        }`,
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        fontFamily: "'Fira Mono', monospace",
        fontSize: '14px',
        fontWeight: '600'
      }}
    >
      <span style={{ fontSize: '20px' }}>
        {categoryColor && icon.includes('⬜') ? (
          <span style={{ 
            display: 'inline-block',
            width: '20px',
            height: '20px',
            borderRadius: '4px',
            background: categoryColor,
            opacity: 0.3,
            border: '2px solid rgba(0,0,0,0.2)'
          }} />
        ) : categoryColor && icon.includes('✅') ? (
          <span style={{ 
            display: 'inline-block',
            width: '20px',
            height: '20px',
            borderRadius: '4px',
            background: categoryColor,
            border: '2px solid white',
            boxShadow: `0 0 8px ${categoryColor}`
          }} />
        ) : (
          icon
        )}
      </span>
      <span style={{ fontWeight: '600' }}>{label}</span>
    </div>
  )
})