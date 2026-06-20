// src/components/BackgroundAnimation.js
import React from 'react';
import Lottie from 'lottie-react';

const BackgroundAnimation = ({ 
  animationData, 
  speed = 0.5,
  opacity = 0.8 
}) => {
  if (!animationData) {
    // Fallback al gradiente original si no hay animación
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%)',
        zIndex: 1
      }} />
    );
  }

  return (
    <>
      {/* Fondo base sólido para evitar espacios blancos */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 25%, #3b82f6 50%, #60a5fa 75%, #93c5fd 100%)',
        zIndex: 0
      }} />
      
      {/* Animación del océano */}
      <div style={{
        position: 'fixed',
        top: '-10%',
        left: '-10%',
        width: '120vw',
        height: '120vh',
        zIndex: 1,
        opacity: opacity,
        overflow: 'hidden'
      }}>
        <Lottie 
          animationData={animationData}
          loop={true}
          autoplay={true}
          speed={speed}
          style={{ 
            width: '100%', 
            height: '100%',
            objectFit: 'cover',
            minWidth: '100vw',
            minHeight: '100vh'
          }}
        />
      </div>
      
      {/* Overlay sutil para asegurar legibilidad y mejorar contraste */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: `
          radial-gradient(circle at 30% 20%, rgba(0, 40, 80, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 70% 80%, rgba(0, 20, 60, 0.1) 0%, transparent 50%),
          rgba(0, 30, 70, 0.05)
        `,
        zIndex: 2
      }} />
    </>
  );
};

export default BackgroundAnimation;