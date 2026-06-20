// src/components/Login.jsx
import React, { useState } from 'react'
import TurtleAnimation from './TurtleAnimation'
import BackgroundAnimation from './BackgroundAnimation'
import turtleAnimationData from '../animations/meditating-turtle.json'
import oceanAnimationData from '../animations/underwater-ocean-turtle.json'

export default function Login({ onLogin }) {
  const [rol, setRol] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    console.log('🔍 Formulario enviado con:', { rol, password })

    try {
      // Llamar a la función login del hook useAuth
      await onLogin(rol, password)
      console.log('✅ Login completado exitosamente')
    } catch (err) {
      console.error('❌ Error en login:', err)
      setError(err.message || 'Error de autenticación')
      setLoading(false)
    }
  }

  return (
    <>
      <div style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: "'Fira Mono', monospace",
        position: 'relative',
        overflow: 'hidden',
        margin: 0,
        padding: 0
      }}>
        
        {/* 🌊 Fondo animado del océano mejorado - Cubre toda la pantalla */}
        <BackgroundAnimation
          animationData={oceanAnimationData}
          speed={0.7}
          opacity={0.95}
        />

        {/* Partículas decorativas de fondo */}
        <div style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          overflow: 'hidden',
          pointerEvents: 'none',
          zIndex: 3
        }}>
          {[...Array(25)].map((_, i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                width: Math.random() * 6 + 2 + 'px',
                height: Math.random() * 6 + 2 + 'px',
                backgroundColor: 'rgba(255,255,255,0.4)',
                borderRadius: '50%',
                left: Math.random() * 100 + '%',
                top: Math.random() * 100 + '%',
                animation: `floatParticles ${Math.random() * 4 + 3}s ease-in-out infinite`
              }}
            />
          ))}
        </div>

        {/* Créditos del proyecto - Movidos fuera del formulario, esquina inferior izquierda */}
        <div style={{
          position: 'absolute',
          bottom: '30px',
          left: '30px',
          background: 'rgba(255, 255, 255, 0.92)',
          padding: '18px 24px',
          borderRadius: '16px',
          boxShadow: '0 8px 25px rgba(0,0,0,0.2)',
          backdropFilter: 'blur(20px)',
          border: '2px solid rgba(255,255,255,0.4)',
          fontSize: '12px',
          color: '#6b7280',
          fontFamily: "'Fira Mono', monospace",
          zIndex: 8,
          maxWidth: '220px'
        }}>
          <div style={{ 
            fontWeight: '600', 
            marginBottom: '8px',
            color: '#374151',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px'
          }}>
            <span>💻</span>
            Desarrollado por:
          </div>
          <div style={{ lineHeight: '1.6' }}>
            <div>👨‍💻 Kevin Vargas</div>
            <div>👨‍💻 Pier Colina</div>
          </div>
        </div>

        {/* 🐢 Tortuga Izquierda */}
        <div style={{
          position: 'absolute',
          left: '6%',
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 5
        }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '50%',
            padding: '30px',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 15px 50px rgba(0,0,0,0.2)',
            border: '3px solid rgba(255,255,255,0.3)',
            animation: 'floatSlow 6s ease-in-out infinite'
          }}>
            <TurtleAnimation
              animationData={turtleAnimationData}
              width={200}
              height={200}
              speed={0.8}
              style={{
                filter: 'drop-shadow(0 8px 16px rgba(0,0,0,0.4)) hue-rotate(120deg) saturate(1.3)',
                transition: 'all 0.3s ease'
              }}
            />
          </div>
        </div>

        {/* 🐢 Tortuga Derecha */}
        <div style={{
          position: 'absolute',
          right: '6%',
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 5
        }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '50%',
            padding: '30px',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 15px 50px rgba(0,0,0,0.2)',
            border: '3px solid rgba(255,255,255,0.3)',
            animation: 'floatSlow 6s ease-in-out infinite 3s'
          }}>
            <TurtleAnimation
              animationData={turtleAnimationData}
              width={200}
              height={200}
              speed={0.6}
              style={{
                filter: 'drop-shadow(0 8px 16px rgba(0,0,0,0.4)) hue-rotate(240deg) saturate(1.4)',
                transform: 'scaleX(-1)',
                transition: 'all 0.3s ease'
              }}
            />
          </div>
        </div>

        {/* Formulario de login mejorado */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.98)',
          padding: '50px',
          borderRadius: '30px',
          boxShadow: '0 30px 60px rgba(0,0,0,0.4)',
          backdropFilter: 'blur(25px)',
          border: '3px solid rgba(255,255,255,0.4)',
          minWidth: '450px',
          maxWidth: '500px',
          textAlign: 'center',
          position: 'relative',
          zIndex: 10,
          animation: 'slideUp 0.8s ease-out',
          margin: '20px'
        }}>
          {/* Logo/Título */}
          <div style={{ marginBottom: '35px' }}>
            <div style={{
              fontSize: '70px',
              marginBottom: '15px',
              animation: 'pulse 2s ease-in-out infinite'
            }}>
              🎓
            </div>
            <h1 style={{
              margin: '0 0 8px 0',
              fontSize: '32px',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Sistema IoT ESPOL
            </h1>
            <p style={{
              margin: 0,
              color: '#6b7280',
              fontSize: '18px',
              fontWeight: '500'
            }}>
              LABORATORIOS FIEC 11C
            </p>
          </div>

          {/* Formulario */}
          <form onSubmit={handleSubmit}>
            {/* Selector de Rol */}
            <div style={{ marginBottom: '25px', textAlign: 'left' }}>
              <label style={{
                display: 'block',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '600',
                color: '#374151'
              }}>
                👤 Rol de Usuario
              </label>
              <select
                value={rol}
                onChange={(e) => setRol(e.target.value)}
                required
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '16px 20px',
                  borderRadius: '15px',
                  border: '2px solid #e5e7eb',
                  fontSize: '16px',
                  fontFamily: "'Fira Mono', monospace",
                  background: loading ? '#f9fafb' : 'white',
                  transition: 'all 0.3s ease',
                  outline: 'none',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1
                }}
                onFocus={(e) => {
                  if (!loading) {
                    e.target.style.borderColor = '#667eea'
                    e.target.style.boxShadow = '0 0 0 4px rgba(102, 126, 234, 0.15)'
                    e.target.style.transform = 'translateY(-1px)'
                  }
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#e5e7eb'
                  e.target.style.boxShadow = 'none'
                  e.target.style.transform = 'translateY(0)'
                }}
              >
                <option value="">Seleccionar rol...</option>
                <option value="estudiante">👨‍🎓 Estudiante</option>
                <option value="profesor">👨‍🏫 Profesor</option>
              </select>
            </div>

            {/* Campo de Contraseña */}
            <div style={{ marginBottom: '25px', textAlign: 'left' }}>
              <label style={{
                display: 'block',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '600',
                color: '#374151'
              }}>
                🔒 Contraseña
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                placeholder="Ingrese su contraseña"
                style={{
                  width: '100%',
                  padding: '16px 20px',
                  borderRadius: '15px',
                  border: '2px solid #e5e7eb',
                  fontSize: '16px',
                  fontFamily: "'Fira Mono', monospace",
                  background: loading ? '#f9fafb' : 'white',
                  transition: 'all 0.3s ease',
                  outline: 'none',
                  boxSizing: 'border-box',
                  cursor: loading ? 'not-allowed' : 'text',
                  opacity: loading ? 0.7 : 1
                }}
                onFocus={(e) => {
                  if (!loading) {
                    e.target.style.borderColor = '#667eea'
                    e.target.style.boxShadow = '0 0 0 4px rgba(102, 126, 234, 0.15)'
                    e.target.style.transform = 'translateY(-1px)'
                  }
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#e5e7eb'
                  e.target.style.boxShadow = 'none'
                  e.target.style.transform = 'translateY(0)'
                }}
              />
            </div>

            {/* Mensaje de Error */}
            {error && (
              <div style={{
                background: 'linear-gradient(135deg, #fee2e2, #fecaca)',
                color: '#dc2626',
                padding: '15px',
                borderRadius: '12px',
                marginBottom: '25px',
                fontSize: '14px',
                fontWeight: '500',
                border: '1px solid #fca5a5',
                animation: 'shake 0.5s ease-in-out'
              }}>
                ⚠️ {error}
              </div>
            )}

            {/* Botón de Login */}
            <button
              type="submit"
              disabled={loading || !rol || !password}
              style={{
                width: '100%',
                padding: '18px',
                borderRadius: '15px',
                border: 'none',
                background: loading || !rol || !password
                  ? '#9ca3af'
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                fontSize: '18px',
                fontWeight: '600',
                cursor: loading || !rol || !password ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                fontFamily: "'Fira Mono', monospace",
                transform: loading ? 'none' : 'translateY(0)',
                boxShadow: loading || !rol || !password
                  ? 'none'
                  : '0 6px 20px rgba(102, 126, 234, 0.4)'
              }}
              onMouseEnter={(e) => {
                if (!loading && rol && password) {
                  e.target.style.transform = 'translateY(-3px)'
                  e.target.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.6)'
                }
              }}
              onMouseLeave={(e) => {
                if (!loading && rol && password) {
                  e.target.style.transform = 'translateY(0)'
                  e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.4)'
                }
              }}
            >
              {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
                  <div style={{
                    width: '22px',
                    height: '22px',
                    border: '3px solid transparent',
                    borderTop: '3px solid white',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                  Iniciando sesión...
                </div>
              ) : (
                '🚀 Ingresar al Sistema'
              )}
            </button>
          </form>

          {/* Imagen de ESPOL - Ahora con más espacio */}
          <div style={{
            marginTop: '35px',
            textAlign: 'center',
            borderRadius: '18px',
            overflow: 'hidden',
            boxShadow: '0 8px 25px rgba(0,0,0,0.2)'
          }}>
            <img 
              src="/espol-image.jpg" 
              alt="ESPOL - Escuela Superior Politécnica del Litoral"
              style={{
                width: '100%',
                height: '220px',
                objectFit: 'cover',
                background: 'linear-gradient(135deg, #f3f4f6, #e5e7eb)',
                transition: 'transform 0.3s ease'
              }}
              onError={(e) => {
                e.target.style.display = 'none'
                e.target.nextSibling.style.display = 'flex'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'scale(1.03)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'scale(1)'
              }}
            />
            {/* Placeholder si no carga la imagen */}
            <div style={{
              display: 'none',
              width: '100%',
              height: '220px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '60px',
              flexDirection: 'column',
              gap: '10px'
            }}>
              <div>🎓</div>
              <div style={{ fontSize: '18px', fontWeight: '600' }}>ESPOL</div>
            </div>
          </div>
        </div>
      </div>

      {/* Estilos CSS mejorados */}
      <style jsx>{`
        body, html {
          margin: 0;
          padding: 0;
          overflow-x: hidden;
        }

        @keyframes floatParticles {
          0%, 100% { 
            transform: translateY(0px) rotate(0deg); 
            opacity: 0.6;
          }
          50% { 
            transform: translateY(-25px) rotate(180deg); 
            opacity: 1;
          }
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @keyframes floatSlow {
          0%, 100% { 
            transform: translateY(-50%) translateX(0) rotate(0deg); 
          }
          50% { 
            transform: translateY(-55%) translateX(8px) rotate(3deg); 
          }
        }

        @keyframes slideUp {
          0% {
            opacity: 0;
            transform: translateY(60px) scale(0.95);
          }
          100% {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.08);
          }
        }

        @keyframes shake {
          0%, 100% {
            transform: translateX(0);
          }
          25% {
            transform: translateX(-6px);
          }
          75% {
            transform: translateX(6px);
          }
        }
      `}</style>
    </>
  )
}