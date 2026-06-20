// src/components/Toast.jsx
import React from 'react'

export default function Toast({ toasts, onRemove }) {
  return (
    <div
      style={{
        position: 'fixed',
        top: '80px', // ⬅️ CAMBIO: de '20px' a '80px' para aparecer debajo del header
        right: '20px',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}
    >
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          style={{
            background: getToastBackground(toast.type),
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            minWidth: '250px',
            maxWidth: '400px',
            animation: 'slideIn 0.3s ease',
            cursor: 'pointer',
            fontFamily: "'Fira Mono', monospace",
            fontSize: '14px'
          }}
          onClick={() => onRemove(toast.id)}
        >
          <span style={{ fontSize: '18px' }}>{getToastIcon(toast.type)}</span>
          <span style={{ flex: 1 }}>{toast.message}</span>
          <span style={{ opacity: 0.7, fontSize: '12px' }}>✕</span>
        </div>
      ))}
      
      <style jsx>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}

function getToastBackground(type) {
  switch (type) {
    case 'success':
      return 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
    case 'error':
      return 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
    case 'warning':
      return 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
    case 'info':
    default:
      return 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
  }
}

function getToastIcon(type) {
  switch (type) {
    case 'success':
      return '✅'
    case 'error':
      return '❌'
    case 'warning':
      return '⚠️'
    case 'info':
    default:
      return 'ℹ️'
  }
}