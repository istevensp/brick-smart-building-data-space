// src/components/TurboNode.jsx
import React, { memo, useEffect, useRef, useState } from 'react'
import { Handle, Position } from 'reactflow'

export default memo(function TurboNode({ data, selected }) {
  const { isDarkMode = true, categoryColor, icon, showIconInCloud, isSensor, onChartClick } = data
  const titleRef = useRef(null)
  const [titleFontSize, setTitleFontSize] = useState(24)
  const [showTooltip, setShowTooltip] = useState(false)
  
  // Auto-ajustar tamaño de fuente del título
  useEffect(() => {
    if (titleRef.current && data.title) {
      const element = titleRef.current
      const maxWidth = 260
      
      element.style.fontSize = '24px'
      
      if (element.scrollWidth > maxWidth) {
        const ratio = maxWidth / element.scrollWidth
        const newSize = Math.max(14, Math.floor(24 * ratio))
        setTitleFontSize(newSize)
      } else {
        setTitleFontSize(24)
      }
    }
  }, [data.title])
  
  // Handle cloud click for charts
  const handleCloudClick = (e) => {
    e.stopPropagation()
    if (isSensor && onChartClick) {
      onChartClick()
    }
  }
  
  // ✅ NUEVO: Información de direcciones para tooltips (según ontología)
  const getTooltipInfo = () => {
    const title = data.title
    if (title === 'Escuela Superior Politécnica del Litoral (ESPOL)') {
      return {
        address: 'Prosperina, Km 30.5 de la Vía Perimetral',
        city: 'Guayaquil',
        country: 'Ecuador',
        postalCode: 'EC090112'
      }
    } else if (title === 'Facultad de Ingeniería en Electricidad y Computación (FIEC)') {
      return {
        address: 'V24J+4RX',
        city: 'Guayaquil', 
        country: 'Ecuador',
        postalCode: 'EC090112'
      }
    }
    return null
  }
  
  const tooltipInfo = getTooltipInfo()
  
  // Estilos dinámicos según el modo
  const nodeStyle = {
    '--gradient-color-1': isDarkMode ? '#e92a67' : '#ff6b9d',
    '--gradient-color-2': isDarkMode ? '#a853ba' : '#c77dff',
    '--gradient-color-3': isDarkMode ? '#2a8af6' : '#7209b7',
    '--inner-bg': isDarkMode 
      ? 'linear-gradient(135deg, rgba(17,17,17,0.95) 0%, rgba(30,30,30,0.95) 100%)' 
      : 'linear-gradient(135deg, rgba(255,251,247,0.95) 0%, rgba(252,248,243,0.95) 100%)',
    '--text-primary': isDarkMode ? 'rgb(243,244,246)' : '#1f2937',
    '--text-secondary': isDarkMode ? '#a1a1a1' : '#6b7280',
    '--footer-color': categoryColor || (isDarkMode ? '#4ade80' : '#10b981'),
    '--cloud-bg': isDarkMode 
      ? 'linear-gradient(135deg, rgb(17,17,17) 0%, rgb(30,30,30) 100%)' 
      : 'linear-gradient(135deg, #fef9f3 0%, #fcf8f3 100%)',
    '--node-shadow': isDarkMode 
      ? '0 10px 30px rgba(42,138,246,0.4), 0 5px 15px rgba(233,42,103,0.3)'
      : '0 10px 30px rgba(139,92,131,0.15), 0 5px 15px rgba(102,126,234,0.1)',
    '--icon-bg': categoryColor 
      ? `linear-gradient(135deg, ${categoryColor}20 0%, ${categoryColor}10 100%)`
      : isDarkMode 
        ? 'linear-gradient(135deg, rgba(168,83,186,0.1) 0%, rgba(42,138,246,0.1) 100%)'
        : 'linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%)',
    // ✅ NUEVO: Estilo mejorado para el círculo de sensores
    '--sensor-circle-bg': isSensor 
      ? (isDarkMode 
          ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
          : 'linear-gradient(135deg, #34d399 0%, #10b981 100%)')
      : 'var(--cloud-bg)',
    '--sensor-circle-shadow': isSensor 
      ? '0 4px 12px rgba(16, 185, 129, 0.4)'
      : 'var(--node-shadow)'
  }
  
  // Función para dividir título largo en múltiples líneas
  const formatTitle = (title) => {
    if (!title) return ''
    
    if (title.length > 30) {
      const breakPoints = ['-', '_', ' ']
      let bestBreakIndex = -1
      let bestBreakChar = ''
      
      const targetIndex = Math.floor(title.length / 2)
      let minDistance = title.length
      
      breakPoints.forEach(char => {
        const index = title.indexOf(char, targetIndex - 10)
        if (index > 0 && Math.abs(index - targetIndex) < minDistance) {
          minDistance = Math.abs(index - targetIndex)
          bestBreakIndex = index
          bestBreakChar = char
        }
      })
      
      if (bestBreakIndex > 0) {
        const part1 = title.substring(0, bestBreakIndex + (bestBreakChar === ' ' ? 0 : 1))
        const part2 = title.substring(bestBreakIndex + 1)
        return (
          <>
            <div>{part1}</div>
            <div>{part2}</div>
          </>
        )
      }
    }
    
    return title
  }
  
  return (
    <div className="react-flow__node-turbo" style={nodeStyle}>
      {/* ✅ NUEVO: Tooltip para direcciones */}
      {tooltipInfo && showTooltip && (
        <div style={{
          position: 'absolute',
          top: '-120px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: isDarkMode ? 'rgba(17,17,17,0.95)' : 'rgba(255,255,255,0.95)',
          color: isDarkMode ? '#f3f4f6' : '#1f2937',
          padding: '12px 16px',
          borderRadius: '8px',
          boxShadow: '0 8px 25px rgba(0,0,0,0.3)',
          border: `1px solid ${isDarkMode ? '#e92a67' : '#667eea'}30`,
          fontSize: '12px',
          zIndex: 1000,
          minWidth: '200px',
          backdropFilter: 'blur(10px)',
          pointerEvents: 'none'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '6px', color: isDarkMode ? '#e92a67' : '#667eea' }}>
            📍 Dirección
          </div>
          <div style={{ marginBottom: '2px' }}>{tooltipInfo.address}</div>
          <div style={{ marginBottom: '2px' }}>{tooltipInfo.city}, {tooltipInfo.country}</div>
          <div style={{ color: isDarkMode ? '#a1a1a1' : '#6b7280' }}>📮 {tooltipInfo.postalCode}</div>
        </div>
      )}

      {/* ✅ MEJORADA: Nube decorativa con círculo verde para sensores */}
      <div 
        className={`cloud ${isDarkMode ? 'gradient' : 'light-gradient'}`}
        onClick={handleCloudClick}
        style={{ 
          cursor: isSensor ? 'pointer' : 'default',
          // Aplicar estilo especial para sensores
          background: isSensor 
            ? 'var(--sensor-circle-bg)' 
            : undefined,
          boxShadow: isSensor 
            ? 'var(--sensor-circle-shadow)'
            : undefined,
          transition: 'all 0.3s ease'
        }}
        title={isSensor ? 'Clic para ver gráfica histórica' : ''}
      >
        <div style={{ 
          background: isSensor ? 'transparent' : 'var(--cloud-bg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          height: '100%',
          borderRadius: '50%'
        }}>
          {isSensor ? (
            // ✅ NUEVO: Diseño especial para sensores con ícono "+" más visible
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '100%',
              height: '100%',
              position: 'relative'
            }}>
              <span style={{ 
                fontSize: '24px',
                fontWeight: 'bold',
                color: 'white',
                textShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }}>
                +
              </span>
              {/* Pequeño ícono de gráfica como indicador adicional */}
              <span style={{
                position: 'absolute',
                bottom: '2px',
                right: '2px',
                fontSize: '8px',
                opacity: 0.8
              }}>
                📊
              </span>
            </div>
          ) : showIconInCloud && icon ? (
            <span style={{ 
              fontSize: '20px',
              filter: 'none',
              transform: 'scale(1)'
            }}>
              {icon}
            </span>
          ) : (
            <span style={{ 
              fontSize: '20px',
              color: categoryColor || 'var(--text-primary)'
            }}>
              •
            </span>
          )}
        </div>
      </div>

      {/* Indicador lateral con gradiente */}
      <div style={{
        position: 'absolute',
        left: '-12px',
        top: '50%',
        transform: 'translateY(-50%)',
        width: '24px',
        height: '24px',
        borderRadius: '50%',
        background: isDarkMode
          ? 'linear-gradient(135deg, #e92a67 0%, #a853ba 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        fontSize: '12px',
        zIndex: 10
      }}>
        {categoryColor ? (
          <span style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: categoryColor,
            border: '1px solid rgba(255,255,255,0.3)'
          }} />
        ) : (
          '•'
        )}
      </div>

      {/* Wrapper con gradiente */}
      <div 
        className={`wrapper ${isDarkMode ? 'gradient' : 'light-gradient'} ${selected ? 'selected' : ''}`}
        onMouseEnter={() => tooltipInfo && setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <div className="inner" style={{ 
          background: 'var(--inner-bg)',
          color: 'var(--text-primary)',
          padding: '14px 18px',
          minHeight: '170px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          backdropFilter: 'blur(10px)'
        }}>
          <div className="body" style={{ width: '100%' }}>
            <div style={{ width: '100%' }}>
              <div 
                ref={titleRef}
                className="title" 
                style={{ 
                  color: 'var(--text-primary)',
                  fontSize: `${titleFontSize}px`,
                  fontWeight: '700',
                  lineHeight: '1.1',
                  marginBottom: data.subtitle ? '6px' : '12px',
                  wordBreak: 'break-word',
                  hyphens: 'auto',
                  textAlign: 'center',
                  transition: 'font-size 0.2s ease',
                  textShadow: isDarkMode 
                    ? '0 2px 4px rgba(0,0,0,0.3)' 
                    : '0 1px 2px rgba(0,0,0,0.1)'
                }}
              >
                {formatTitle(data.title)}
              </div>
              
              {data.subtitle && (
                <div 
                  className="subtitle" 
                  style={{ 
                    color: 'var(--text-secondary)',
                    fontSize: '16px',
                    lineHeight: '1.3',
                    marginBottom: data.footer ? '8px' : '0',
                    textAlign: 'center',
                    opacity: 0.8
                  }}
                >
                  {data.subtitle}
                </div>
              )}
              
              {data.footer && (
                <div 
                  className="footer" 
                  style={{ 
                    color: 'var(--footer-color)',
                    fontSize: '18px',
                    fontWeight: '600',
                    textAlign: 'center',
                    lineHeight: '1.2',
                    marginTop: '4px',
                    textShadow: isDarkMode 
                      ? '0 2px 4px rgba(0,0,0,0.3)' 
                      : '0 1px 2px rgba(0,0,0,0.1)',
                    background: `linear-gradient(135deg, ${categoryColor || '#4ade80'}15 0%, ${categoryColor || '#10b981'}10 100%)`,
                    padding: '4px 8px',
                    borderRadius: '6px',
                    backdropFilter: 'blur(5px)',
                    border: `1px solid ${categoryColor || (isDarkMode ? '#4ade80' : '#10b981')}30`
                  }}
                >
                  {data.footer}
                </div>
              )}
            </div>
          </div>
          <Handle type="target" position={Position.Left} />
          <Handle type="source" position={Position.Right} />
        </div>
      </div>
      
      <style jsx>{`
        .react-flow__node-turbo {
          min-width: 300px;
          min-height: 170px;
          max-width: 380px;
          border-radius: 16px;
          transition: all 0.3s ease;
        }
        
        .react-flow__node-turbo:hover {
          transform: translateY(-2px);
          box-shadow: var(--node-shadow);
        }
        
        .cloud {
          border-radius: 100%;
          width: 45px;
          height: 45px;
          position: absolute;
          top: 0;
          right: 0;
          transform: translate(50%,-50%);
          box-shadow: var(--node-box-shadow);
          overflow: hidden;
          padding: 2px;
          z-index: 20;
          transition: all 0.3s ease;
        }
        
        .cloud:hover {
          transform: translate(50%,-50%) scale(1.1);
          box-shadow: ${isSensor ? '0 6px 20px rgba(16, 185, 129, 0.6)' : 'var(--node-shadow)'};
        }
        
        .wrapper {
          border-radius: 14px;
        }
        
        .inner {
          border-radius: 12px;
        }
        
        .gradient:before {
          content: '';
          position: absolute;
          padding-bottom: calc(100% * 1.41421356237);
          width: calc(100% * 1.41421356237);
          background: conic-gradient(
            from -160deg at 50% 50%,
            var(--gradient-color-1) 0deg,
            var(--gradient-color-2) 120deg,
            var(--gradient-color-3) 240deg,
            var(--gradient-color-1) 360deg
          );
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          border-radius: 100%;
          pointer-events: none;
        }
        
        .light-gradient:before {
          content: '';
          position: absolute;
          padding-bottom: calc(100% * 1.41421356237);
          width: calc(100% * 1.41421356237);
          background: linear-gradient(
            135deg,
            #667eea 0%,
            #764ba2 25%,
            #f093fb 50%,
            #f5576c 75%,
            #667eea 100%
          );
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          border-radius: 100%;
          pointer-events: none;
          opacity: 0.8;
        }
        
        .wrapper.gradient.selected:before,
        .wrapper.light-gradient.selected:before,
        .cloud.gradient.selected:before,
        .cloud.light-gradient.selected:before {
          animation: spinner 4s linear infinite;
        }
        
        @keyframes spinner {
          100% { 
            transform: translate(-50%, -50%) rotate(-360deg); 
          }
        }
        
        .react-flow__node-turbo.selected {
          animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
          0% {
            box-shadow: var(--node-shadow);
          }
          50% {
            box-shadow: 
              0 0 30px rgba(42, 138, 246, 0.6),
              0 0 60px rgba(233, 42, 103, 0.4);
          }
          100% {
            box-shadow: var(--node-shadow);
          }
        }
      `}</style>
    </div>
  )
})





