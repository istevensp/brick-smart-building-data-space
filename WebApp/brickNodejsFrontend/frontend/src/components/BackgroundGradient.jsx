// src/components/BackgroundGradient.jsx
import React from 'react'

export default function BackgroundGradient({ isDarkMode }) {
  if (isDarkMode) {
    return null // En modo oscuro usamos el fondo normal
  }

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(circle at 20% 20%, rgba(147, 197, 253, 0.25) 0%, transparent 35%),
          radial-gradient(circle at 80% 30%, rgba(196, 181, 253, 0.22) 0%, transparent 35%),
          radial-gradient(circle at 40% 70%, rgba(252, 165, 165, 0.18) 0%, transparent 35%),
          radial-gradient(circle at 90% 80%, rgba(134, 239, 172, 0.2) 0%, transparent 35%),
          radial-gradient(circle at 10% 90%, rgba(254, 202, 202, 0.18) 0%, transparent 35%),
          radial-gradient(circle at 70% 10%, rgba(165, 180, 252, 0.15) 0%, transparent 35%),
          radial-gradient(circle at 60% 50%, rgba(251, 207, 232, 0.12) 0%, transparent 30%),
          linear-gradient(135deg, 
            #f1f5f9 0%, 
            #f8fafc 12%,
            #fefce8 25%,
            #eff6ff 37%,
            #fdf4ff 50%,
            #f0fdf4 62%,
            #fef7ed 75%,
            #f5f3ff 87%,
            #f1f5f9 100%
          )
        `,
        pointerEvents: 'none',
        zIndex: -1
      }}
    />
  )
}