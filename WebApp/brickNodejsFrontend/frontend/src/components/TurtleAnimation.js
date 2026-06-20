// src/components/TurtleAnimation.js
import React from 'react';
import Lottie from 'lottie-react';

const TurtleAnimation = ({ 
  animationData, 
  width = 200, 
  height = 200, 
  loop = true, 
  autoplay = true,
  speed = 1,
  style = {},
  className = ""
}) => {
  if (!animationData) {
    return (
      <div 
        style={{
          width: width,
          height: height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(16, 185, 129, 0.1)',
          borderRadius: '50%',
          border: '2px dashed #10b981',
          color: '#10b981',
          fontSize: '14px',
          fontWeight: '600',
          textAlign: 'center',
          flexDirection: 'column',
          ...style
        }}
        className={className}
      >
        <div style={{ fontSize: '32px', marginBottom: '8px' }}>🐢</div>
        <div>Cargando...</div>
      </div>
    );
  }

  return (
    <div 
      style={{
        width: width,
        height: height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        ...style
      }}
      className={className}
    >
      <Lottie 
        animationData={animationData}
        loop={loop}
        autoplay={autoplay}
        style={{ 
          width: '100%', 
          height: '100%',
          maxWidth: width,
          maxHeight: height
        }}
      />
    </div>
  );
};

export default TurtleAnimation;