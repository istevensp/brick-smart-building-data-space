import React from 'react'
import { BaseEdge, getSmoothStepPath } from 'reactflow'

export function AnimatedSVGEdge({
  id, sourceX, sourceY, sourcePosition,
  targetX, targetY, targetPosition,
  animated = false
}) {
  const [edgePath] = getSmoothStepPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition
  })

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd="url(#edge-circle)"
        style={{ 
          stroke: 'url(#edge-gradient)', 
          strokeWidth: 2,
          strokeDasharray: animated ? '5,5' : 'none',
          animation: animated ? 'dashdraw 1s linear infinite' : 'none'
        }}
      />
      {animated && (
        <>
          {/* Círculo animado que se mueve por el edge */}
          <circle r="4" fill="#e92a67">
            <animateMotion dur="2s" repeatCount="indefinite" path={edgePath} />
          </circle>
          {/* Segundo círculo para mayor efecto visual */}
          <circle r="3" fill="#a853ba">
            <animateMotion dur="2s" repeatCount="indefinite" path={edgePath} begin="0.5s" />
          </circle>
          {/* Tercer círculo */}
          <circle r="2" fill="#2a8af6">
            <animateMotion dur="2s" repeatCount="indefinite" path={edgePath} begin="1s" />
          </circle>
        </>
      )}
    </>
  )
}









