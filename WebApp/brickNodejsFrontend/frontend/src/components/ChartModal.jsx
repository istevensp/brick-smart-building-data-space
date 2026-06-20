// src/components/ChartModal.jsx
import React, { useState, useEffect, useRef } from 'react'
import Chart from 'chart.js/auto'
import api from '../api'

export default function ChartModal({ sensor, onClose, isDarkMode }) {
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [interval, setInterval] = useState('d')
  const [loading, setLoading] = useState(false)
  const [chartData, setChartData] = useState(null)
  const [showChart, setShowChart] = useState(false)
  const chartRef = useRef(null)
  const chartInstance = useRef(null)

  // Set default dates (last 7 days)
  useEffect(() => {
    const today = new Date()
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    
    setDateTo(today.toISOString().split('T')[0])
    setDateFrom(lastWeek.toISOString().split('T')[0])
  }, [])

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy()
      }
    }
  }, [])

  // ✅ NUEVA FUNCIÓN: Exportar a CSV
  const exportToCSV = () => {
    if (!chartData || chartData.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    const headers = ['Fecha', 'Valor', 'Unidad', 'Cantidad_Muestras', 'Sensor'];
    
    const csvContent = [
      headers.join(','),
      ...chartData.map(item => {
        const id = item._id || {};
        const year = id.year || new Date().getFullYear();
        const month = id.month || 1;
        const day = id.day || 1;
        const hour = id.hour || 0;
        const minute = id.minute || 0;
        
        let formattedDate = '';
        if (interval === 'd') {
          formattedDate = `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')}/${year}`;
        } else if (interval === 'h') {
          formattedDate = `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')}/${year} ${hour.toString().padStart(2, '0')}:00`;
        } else if (interval === 'm') {
          formattedDate = `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')}/${year} ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        }
        
        return [
          `"${formattedDate}"`,
          item.avg_value || 0,
          `"${sensor.unit || ''}"`,
          item.count || 0,
          `"${sensor.sensor}"`
        ].join(',');
      })
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${sensor.sensor}_${dateFrom}_${dateTo}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // ✅ NUEVA FUNCIÓN: Exportar a JSON
  const exportToJSON = () => {
    if (!chartData || chartData.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    const exportData = {
      sensor: sensor.sensor,
      unit: sensor.unit,
      dateFrom: dateFrom,
      dateTo: dateTo,
      interval: interval,
      totalSamples: chartData.length,
      data: chartData.map(item => {
        const id = item._id || {};
        return {
          year: id.year,
          month: id.month,
          day: id.day,
          hour: id.hour,
          minute: id.minute,
          averageValue: item.avg_value,
          sampleCount: item.count
        };
      }),
      exportedAt: new Date().toISOString()
    };

    const jsonContent = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${sensor.sensor}_${dateFrom}_${dateTo}.json`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const fetchHistoryData = async () => {
    if (!dateFrom || !dateTo) {
      alert('Por favor seleccione las fechas')
      return
    }

    setLoading(true)
    try {
      const response = await api.get(
        `/sensors/history/${sensor.sensor}/${dateFrom}/${dateTo}/${interval}`
      )
      
      console.log('Datos recibidos:', response.data)
      
      if (!response.data || response.data.length === 0) {
        alert('No se encontraron datos para el rango de fechas seleccionado')
        setLoading(false)
        return
      }
      
      const validData = response.data.filter(item => 
        item && 
        item._id && 
        typeof item.avg_value === 'number' && 
        !isNaN(item.avg_value) &&
        item.avg_value !== null &&
        item.avg_value !== undefined
      )
      
      if (validData.length === 0) {
        alert('No se encontraron datos válidos para el rango de fechas seleccionado')
        setLoading(false)
        return
      }
      
      setChartData(validData)
      setShowChart(true)
      
      setTimeout(() => {
        renderChart(validData)
      }, 100)
    } catch (error) {
      console.error('Error fetching history:', error)
      alert('Error al obtener los datos históricos. Verifique que el sensor tenga datos en el rango seleccionado.')
    } finally {
      setLoading(false)
    }
  }

  const renderChart = (data) => {
    if (!chartRef.current || !data || data.length === 0) return

    if (chartInstance.current) {
      chartInstance.current.destroy()
    }

    const ctx = chartRef.current.getContext('2d')
    
    const processedData = data.map(item => {
      const id = item._id || {}
      const year = id.year || new Date().getFullYear()
      const month = id.month || 1
      const day = id.day || 1
      const hour = id.hour || 0
      const minute = id.minute || 0
      
      let label = ''
      if (interval === 'd') {
        label = `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')}/${year}`
      } else if (interval === 'h') {
        label = `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')} ${hour.toString().padStart(2, '0')}:00`
      } else if (interval === 'm') {
        label = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
      } else {
        label = `${day}/${month}/${year}`
      }
      
      return {
        label,
        value: parseFloat(item.avg_value) || 0,
        count: parseInt(item.count) || 0,
        originalItem: item
      }
    })

    const labels = processedData.map(item => item.label)
    const values = processedData.map(item => item.value)

    const validValues = values.filter(v => typeof v === 'number' && !isNaN(v))
    const maxValue = validValues.length > 0 ? Math.max(...validValues) : 0
    const minValue = validValues.length > 0 ? Math.min(...validValues) : 0
    const avgValue = validValues.length > 0 ? validValues.reduce((sum, val) => sum + val, 0) / validValues.length : 0

    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: `${sensor.sensor} - Promedio`,
          data: values,
          borderColor: isDarkMode ? '#e92a67' : '#667eea',
          backgroundColor: isDarkMode ? 'rgba(233, 42, 103, 0.1)' : 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: isDarkMode ? '#a853ba' : '#764ba2',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointHoverRadius: 8,
          pointHoverBackgroundColor: isDarkMode ? '#e92a67' : '#667eea',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          title: {
            display: true,
            text: `Historial de ${sensor.sensor}`,
            color: isDarkMode ? '#fff' : '#333',
            font: {
              size: 18,
              weight: 'bold'
            },
            padding: 20
          },
          legend: {
            display: true,
            labels: {
              color: isDarkMode ? '#fff' : '#333',
              usePointStyle: true,
              padding: 20
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: isDarkMode ? 'rgba(30, 30, 30, 0.95)' : 'rgba(255, 255, 255, 0.95)',
            titleColor: isDarkMode ? '#fff' : '#333',
            bodyColor: isDarkMode ? '#fff' : '#333',
            borderColor: isDarkMode ? '#e92a67' : '#667eea',
            borderWidth: 2,
            cornerRadius: 8,
            padding: 12,
            callbacks: {
              label: function(context) {
                try {
                  const dataIndex = context.dataIndex
                  if (dataIndex >= 0 && dataIndex < processedData.length) {
                    const item = processedData[dataIndex]
                    const value = (item.value || 0).toFixed(3)
                    const count = item.count || 0
                    const label = item.label || 'N/A'
                    
                    return [
                      `Valor: ${value} ${sensor.unit || ''}`,
                      `Muestras: ${count}`,
                      `Fecha: ${label}`
                    ]
                  }
                  return [`Valor: N/A`]
                } catch (error) {
                  console.warn('Error in tooltip callback:', error)
                  return [`Valor: N/A`]
                }
              },
              afterBody: function() {
                try {
                  return [
                    '',
                    `📊 Estadísticas:`,
                    `Máximo: ${maxValue.toFixed(3)}`,
                    `Mínimo: ${minValue.toFixed(3)}`,
                    `Promedio: ${avgValue.toFixed(3)}`
                  ]
                } catch (error) {
                  console.warn('Error in afterBody callback:', error)
                  return ['📊 Estadísticas no disponibles']
                }
              }
            }
          }
        },
        scales: {
          x: {
            display: true,
            grid: {
              color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
              borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)'
            },
            ticks: {
              color: isDarkMode ? '#a1a1a1' : '#6b7280',
              maxRotation: 45,
              minRotation: 45,
              font: {
                size: 11
              }
            },
            title: {
              display: true,
              text: getIntervalLabel(interval),
              color: isDarkMode ? '#fff' : '#333',
              font: {
                size: 13,
                weight: 'bold'
              }
            }
          },
          y: {
            display: true,
            grid: {
              color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
              borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)'
            },
            ticks: {
              color: isDarkMode ? '#a1a1a1' : '#6b7280',
              font: {
                size: 11
              }
            },
            title: {
              display: true,
              text: `Valor (${sensor.unit || ''})`,
              color: isDarkMode ? '#fff' : '#333',
              font: {
                size: 13,
                weight: 'bold'
              }
            }
          }
        }
      }
    })
  }

  const getIntervalLabel = (interval) => {
    const labels = {
      'd': 'Fecha (Por Día)',
      'h': 'Fecha y Hora',  
      'm': 'Hora y Minuto'
    }
    return labels[interval] || 'Fecha'
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{
        background: isDarkMode 
          ? 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)'
          : 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
        borderRadius: '20px',
        padding: '30px',
        width: showChart ? '95%' : '450px',
        maxWidth: showChart ? '1400px' : '450px',
        maxHeight: '95vh',
        overflow: 'auto',
        boxShadow: '0 25px 80px rgba(0, 0, 0, 0.4)',
        border: isDarkMode 
          ? '2px solid rgba(233, 42, 103, 0.3)'
          : '2px solid rgba(102, 126, 234, 0.3)',
        transition: 'all 0.4s ease'
      }}>
        {!showChart ? (
          <>
            <h2 style={{
              color: isDarkMode ? '#fff' : '#333',
              marginBottom: '24px',
              fontSize: '28px',
              fontWeight: 'bold',
              textAlign: 'center',
              fontFamily: "'Fira Mono', monospace"
            }}>
              📈 Análisis Histórico
            </h2>
            
            <div style={{
              marginBottom: '24px',
              padding: '20px',
              background: isDarkMode 
                ? 'rgba(168, 83, 186, 0.15)'
                : 'rgba(102, 126, 234, 0.15)',
              borderRadius: '16px',
              border: `2px solid ${isDarkMode ? '#a853ba' : '#667eea'}40`
            }}>
              <p style={{
                color: isDarkMode ? '#fff' : '#333',
                margin: 0,
                fontSize: '20px',
                fontWeight: '700',
                textAlign: 'center'
              }}>
                🔍 {sensor.sensor}
              </p>
              {sensor.unit && (
                <p style={{
                  color: isDarkMode ? '#a1a1a1' : '#6b7280',
                  margin: '8px 0 0 0',
                  fontSize: '16px',
                  textAlign: 'center'
                }}>
                  📊 Unidad: {sensor.unit}
                </p>
              )}
            </div>

            {/* ✅ MEJORADO: Más padding y margen en los inputs de fecha */}
            <div style={{ marginBottom: '24px', padding: '0 8px' }}>
              <label style={{
                display: 'block',
                color: isDarkMode ? '#fff' : '#333',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '600'
              }}>
                📅 Fecha Inicio:
              </label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                style={{
                  width: '100%',
                  padding: '16px 20px',  /* ✅ Aumentado de 12px 16px */
                  borderRadius: '12px',
                  border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'}`,
                  background: isDarkMode ? 'rgba(0,0,0,0.4)' : 'rgba(255,255,255,0.9)',
                  color: isDarkMode ? '#fff' : '#333',
                  fontSize: '16px',
                  fontFamily: "'Fira Mono', monospace",
                  transition: 'all 0.2s ease',
                  margin: '0 0 8px 0',  /* ✅ Margen inferior agregado */
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px', padding: '0 8px' }}>
              <label style={{
                display: 'block',
                color: isDarkMode ? '#fff' : '#333',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '600'
              }}>
                📅 Fecha Fin:
              </label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                style={{
                  width: '100%',
                  padding: '16px 20px',  /* ✅ Aumentado de 12px 16px */
                  borderRadius: '12px',
                  border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'}`,
                  background: isDarkMode ? 'rgba(0,0,0,0.4)' : 'rgba(255,255,255,0.9)',
                  color: isDarkMode ? '#fff' : '#333',
                  fontSize: '16px',
                  fontFamily: "'Fira Mono', monospace",
                  transition: 'all 0.2s ease',
                  margin: '0 0 8px 0',  /* ✅ Margen inferior agregado */
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{ marginBottom: '28px', padding: '0 8px' }}>
              <label style={{
                display: 'block',
                color: isDarkMode ? '#fff' : '#333',
                marginBottom: '10px',
                fontSize: '16px',
                fontWeight: '600'
              }}>
                ⏱️ Intervalo de Agrupación:
              </label>
              <select
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
                style={{
                  width: '100%',
                  padding: '16px 20px',  /* ✅ Aumentado padding */
                  borderRadius: '12px',
                  border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'}`,
                  background: isDarkMode ? 'rgba(0,0,0,0.4)' : 'rgba(255,255,255,0.9)',
                  color: isDarkMode ? '#fff' : '#333',
                  fontSize: '16px',
                  fontFamily: "'Fira Mono', monospace",
                  cursor: 'pointer',
                  boxSizing: 'border-box'
                }}
              >
                <option value="d">📊 Diario (Promedio por día)</option>
                <option value="h">⏰ Por Hora (Promedio por hora)</option>
                <option value="m">⚡ Por Minuto (Promedio por minuto)</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '12px', padding: '0 8px' }}>
              <button
                onClick={fetchHistoryData}
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '16px 24px',
                  borderRadius: '14px',
                  border: 'none',
                  background: loading 
                    ? 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)'
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#fff',
                  fontSize: '18px',
                  fontWeight: '700',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                  transition: 'all 0.3s ease',
                  fontFamily: "'Fira Mono', monospace",
                  boxShadow: loading ? 'none' : '0 8px 20px rgba(102, 126, 234, 0.3)'
                }}
              >
                {loading ? '⏳ Cargando...' : '📈 Generar Gráfica'}
              </button>
              
              <button
                onClick={onClose}
                style={{
                  padding: '16px 24px',
                  borderRadius: '14px',
                  border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)'}`,
                  background: 'transparent',
                  color: isDarkMode ? '#fff' : '#333',
                  fontSize: '18px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: "'Fira Mono', monospace"
                }}
              >
                ❌ Cancelar
              </button>
            </div>
          </>
        ) : (
          <>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '24px',
              flexWrap: 'wrap',
              gap: '12px'
            }}>
              <h2 style={{
                color: isDarkMode ? '#fff' : '#333',
                fontSize: '24px',
                fontWeight: 'bold',
                fontFamily: "'Fira Mono', monospace",
                margin: 0
              }}>
                📈 {sensor.sensor} - Análisis Histórico
              </h2>
              
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  onClick={() => {
                    setShowChart(false)
                    setChartData(null)
                  }}
                  style={{
                    padding: '10px 20px',
                    borderRadius: '10px',
                    border: 'none',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: '#fff',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    fontFamily: "'Fira Mono', monospace"
                  }}
                >
                  🔄 Nueva Consulta
                </button>
                
                <button
                  onClick={onClose}
                  style={{
                    padding: '10px 20px',
                    borderRadius: '10px',
                    border: 'none',
                    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    color: '#fff',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    fontFamily: "'Fira Mono', monospace"
                  }}
                >
                  ✕ Cerrar
                </button>
              </div>
            </div>
            
            <div style={{
              height: '600px',
              padding: '24px',
              background: isDarkMode 
                ? 'rgba(0, 0, 0, 0.4)'
                : 'rgba(255, 255, 255, 0.6)',
              borderRadius: '20px',
              border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`
            }}>
              <canvas ref={chartRef}></canvas>
            </div>
            
            {/* ✅ NUEVO: Panel de estadísticas */}
            {chartData && (
              <div style={{
                marginTop: '24px',
                padding: '20px',
                background: isDarkMode 
                  ? 'rgba(168, 83, 186, 0.15)'
                  : 'rgba(102, 126, 234, 0.15)',
                borderRadius: '16px',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '20px'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <p style={{
                    color: isDarkMode ? '#a1a1a1' : '#6b7280',
                    margin: 0,
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    📅 Período Analizado
                  </p>
                  <p style={{
                    color: isDarkMode ? '#fff' : '#333',
                    margin: '8px 0 0 0',
                    fontSize: '16px',
                    fontWeight: '700'
                  }}>
                    {dateFrom} → {dateTo}
                  </p>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <p style={{
                    color: isDarkMode ? '#a1a1a1' : '#6b7280',
                    margin: 0,
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    📊 Total de Muestras
                  </p>
                  <p style={{
                    color: isDarkMode ? '#fff' : '#333',
                    margin: '8px 0 0 0',
                    fontSize: '16px',
                    fontWeight: '700'
                  }}>
                    {chartData.length}
                  </p>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <p style={{
                    color: isDarkMode ? '#a1a1a1' : '#6b7280',
                    margin: 0,
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    📊 Promedio General
                  </p>
                  <p style={{
                    color: isDarkMode ? '#fff' : '#333',
                    margin: '8px 0 0 0',
                    fontSize: '16px',
                    fontWeight: '700'
                  }}>
                    {(chartData.reduce((sum, item) => sum + (item.avg_value || 0), 0) / chartData.length).toFixed(3)} {sensor.unit || 'V'}
                  </p>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <p style={{
                    color: isDarkMode ? '#a1a1a1' : '#6b7280',
                    margin: 0,
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    ⏱️ Intervalo
                  </p>
                  <p style={{
                    color: isDarkMode ? '#fff' : '#333',
                    margin: '8px 0 0 0',
                    fontSize: '16px',
                    fontWeight: '700'
                  }}>
                    {getIntervalLabel(interval)}
                  </p>
                </div>
              </div>
            )}

            {/* ✅ NUEVO: Botones de exportación */}
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '12px',
              flexWrap: 'wrap',
              marginTop: '24px'
            }}>
              <button
                onClick={exportToCSV}
                style={{
                  padding: '12px 20px',
                  borderRadius: '10px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#fff',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: "'Fira Mono', monospace",
                  boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 6px 16px rgba(16, 185, 129, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
                }}
              >
                📊 Exportar CSV
              </button>
              
              <button
                onClick={exportToJSON}
                style={{
                  padding: '12px 20px',
                  borderRadius: '10px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                  color: '#fff',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: "'Fira Mono', monospace",
                  boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 6px 16px rgba(245, 158, 11, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 12px rgba(245, 158, 11, 0.3)';
                }}
              >
                🗂️ Exportar JSON
              </button>
              
              <button
                onClick={() => setShowChart(false)}
                style={{
                  padding: '12px 20px',
                  borderRadius: '10px',
                  border: `2px solid ${isDarkMode ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)'}`,
                  background: 'transparent',
                  color: isDarkMode ? '#fff' : '#333',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  fontFamily: "'Fira Mono', monospace"
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'transparent';
                }}
              >
                ⬅️ Volver
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}