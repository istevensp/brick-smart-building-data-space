// src/App.js
import React from 'react'
import FlowDiagram from './components/FlowDiagram'
import Login from './components/Login'
import { useAuth } from './hooks/useAuth'
import './App.css'

function App() {
  const { user, loading, login, logout, isAuthenticated, isProfesor, isEstudiante } = useAuth()

  // Mostrar spinner de carga mientras verifica autenticación
  if (loading) {
    return (
      <div style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontFamily: "'Fira Mono', monospace"
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '60px',
            height: '60px',
            border: '4px solid transparent',
            borderTop: '4px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }} />
          <h2 style={{ margin: 0, fontSize: '24px' }}>Cargando Sistema IoT...</h2>
        </div>
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    )
  }

  // Si no está autenticado, mostrar login
  if (!isAuthenticated) {
    return <Login onLogin={login} />
  }

  // Si está autenticado, mostrar la aplicación principal
  return (
    <div className="App" style={{ position: 'relative' }}>
      {/* Header con información del usuario y logout */}
      <div style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        zIndex: 1001,
        display: 'flex',
        alignItems: 'center',
        gap: '15px',
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '12px 20px',
        borderRadius: '50px',
        boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.2)',
        fontFamily: "'Fira Mono', monospace"
      }}>
        {/* Información del usuario */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '14px',
          fontWeight: '600'
        }}>
          <span style={{ fontSize: '20px' }}>
            {isProfesor ? '👨‍🏫' : '👨‍🎓'}
          </span>
          <span style={{ 
            color: isProfesor ? '#059669' : '#3b82f6',
            textTransform: 'capitalize'
          }}>
            {user.rol}
          </span>
          {isProfesor && (
            <span style={{
              background: 'linear-gradient(135deg, #10b981, #059669)',
              color: 'white',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: '700'
            }}>
              ADMIN
            </span>
          )}
        </div>

        {/* Separador */}
        <div style={{
          width: '1px',
          height: '20px',
          background: '#e5e7eb'
        }} />

        {/* Botón de logout */}
        <button
          onClick={logout}
          style={{
            background: 'linear-gradient(135deg, #ef4444, #dc2626)',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'scale(1.05)'
            e.target.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.4)'
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'scale(1)'
            e.target.style.boxShadow = 'none'
          }}
        >
          <span>🚪</span>
          Salir
        </button>
      </div>

      {/* Componente principal FlowDiagram con rol */}
      <FlowDiagram userRole={user.rol} />
    </div>
  )
}

export default App
