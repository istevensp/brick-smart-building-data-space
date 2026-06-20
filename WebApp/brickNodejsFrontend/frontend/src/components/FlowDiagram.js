// src/components/FlowDiagram.js

import React, { useState, useCallback, useEffect, useMemo, useRef } from 'react'
import ReactFlow, {
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
  Controls,
  Background,
  Position
} from 'reactflow'
import 'reactflow/dist/style.css'
import '../index.css'
import '../turbo.css'

import TurboNode from './TurboNode'
import ControlNode from './ControlNode'
import SearchNode from './SearchNode'
import ChartModal from './ChartModal'
import BackgroundGradient from './BackgroundGradient'
import { AnimatedSVGEdge } from './AnimatedSVGEdge'
import Toast from './Toast'
import AdminPanelModal from './AdminPanelModal' // ✅ NUEVO: Import del Panel Admin
import api from '../api'

const nodeTypes = { 
  turbo: TurboNode,
  control: ControlNode,
  search: SearchNode 
}
const edgeTypes = { animated: AnimatedSVGEdge }

// --------------------------------------------------
// Mapeo de unidades a categorías de sensores
const UNIT_TO_CATEGORY = {
  'W': 'power',           
  'VA': 'power',          
  'VAR': 'power',         
  'A': 'electrical',      
  'V': 'electrical',      
  'DEG_C': 'temperature', 
  'PERCENT_RH': 'humidity', 
  'PA': 'pressure',       
  'PPM': 'air_quality',   
  'IN-PER-SEC': 'weather', 
  'M-PER-SEC': 'weather',  
  'DEG': 'weather',        
  null: 'monitoring'       
}

// Colores para cada categoría
const CATEGORY_COLORS = {
  power: '#fbbf24',
  electrical: '#8b5cf6',
  temperature: '#ef4444',
  humidity: '#3b82f6',
  pressure: '#10b981',
  air_quality: '#06b6d4',
  weather: '#f97316',
  monitoring: '#6b7280'
}

// Nombres amigables para categorías
const CATEGORY_NAMES = {
  power: 'Potencia',
  electrical: 'Eléctrico',
  temperature: 'Temperatura',
  humidity: 'Humedad',
  pressure: 'Presión',
  air_quality: 'Calidad del Aire',
  weather: 'Clima',
  monitoring: 'Monitoreo'
}

// Iconos para nodos según su tipo
const NODE_ICONS = {
  'Escuela Superior Politécnica del Litoral (ESPOL)': '🎓',
  'Facultad de Ingeniería en Electricidad y Computación (FIEC)': '⚡',
  'Edificio FIEC 11-C Laboratorios': '🏢',
  'Edificio 11-C Piso 1': '1️⃣',
  'Edificio 11-C Piso 2': '2️⃣',
  'Laboratorio de IoT y Telemática': '📡',
  'Jardín frontal del lab': '🌳',
  'Laboratorio de Redes de Datos': '🌐',
  'Laboratorio de Sistemas en la Nube': '☁️',
  'default': '📍'
}

// --------------------------------------------------
// Hook para cargar los equipos de cada laboratorio
function useLabEquipments(labId) {
  const [equipments, setEquipments] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!labId) {
      setEquipments([])
      setError(null)
      return
    }

    const controller = new AbortController()

    const filterMap = {
      '11C-LabIoT': { db: '11C-LabIoT', equipment: 'EM-LIoTST' },
      'EST_MET': { db_id: 'EST_MET', equipment: 'EM-LIoTST' },
      '11C-LabRDD': { db: '11C-LabRDD' },
      '11C-LabSN': { db: '11C-LabSN' }
    }

    const filter = filterMap[labId]
    if (!filter) return

    api.get('/sensors/', { signal: controller.signal })
      .then(res => {
        const list = res.data
          .filter(s => s.db === filter.db || s.db_id === filter.db_id)
          .map(s => s.equipment)
        setEquipments([...new Set(list)])
        setError(null)
      })
      .catch(err => {
        if (!controller.signal.aborted) {
          console.error('Error loading lab equipments:', err)
          setEquipments([])
          setError(err.message)
        }
      })

    return () => controller.abort()
  }, [labId])

  return { equipments, error }
}

// --------------------------------------------------
// Hook para cargar los sensores de un equipo específico
function useEquipmentSensors(equipmentId, maxRetries = 3) {
  const [sensors, setSensors] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    if (!equipmentId) {
      setSensors([])
      setError(null)
      return
    }

    const controller = new AbortController()
    
    const fetchSensors = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const res = await api.get(`/equipment/${equipmentId}`, { 
          signal: controller.signal 
        })
        setSensors(res.data)
        setRetryCount(0)
      } catch (err) {
        if (!controller.signal.aborted) {
          console.error('Error loading sensors:', err)
          setSensors([])
          setError(err.message)
          
          if (retryCount < maxRetries) {
            setTimeout(() => {
              setRetryCount(prev => prev + 1)
            }, 1000 * (retryCount + 1))
          }
        }
      } finally {
        setLoading(false)
      }
    }

    fetchSensors()
    
    return () => controller.abort()
  }, [equipmentId, retryCount, maxRetries])

  return { sensors, loading, error }
}

// --------------------------------------------------
// Hook para obtener todos los sensores de todos los equipos
function useAllEquipmentsSensors(equipments) {
  const [allSensors, setAllSensors] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!equipments || equipments.length === 0) {
      setAllSensors({})
      return
    }

    const controller = new AbortController()

    const fetchAllSensors = async () => {
      setLoading(true)
      const sensorsMap = {}

      try {
        const promises = equipments.map(async (equipment) => {
          try {
            const res = await api.get(`/equipment/${equipment}`, {
              signal: controller.signal
            })
            return { equipment, sensors: res.data }
          } catch {
            return { equipment, sensors: [] }
          }
        })

        const results = await Promise.all(promises)
        results.forEach(({ equipment, sensors }) => {
          sensorsMap[equipment] = sensors
        })

        setAllSensors(sensorsMap)
      } catch (err) {
        console.error('Error fetching all sensors:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAllSensors()

    return () => controller.abort()
  }, [equipments])

  return { allSensors, loading }
}

// --------------------------------------------------
// Hook optimizado con batch loading
function useMultipleSensorsData(sensors, refreshInterval = null) {
  const [sensorsData, setSensorsData] = useState({})
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (!sensors || sensors.length === 0) {
      setSensorsData({})
      setErrors({})
      return
    }

    const controller = new AbortController()

    const fetchAllSensors = async () => {
      setLoading(true)
      
      const promises = sensors.map(sensor => {
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 5000)
        )
        
        const fetchPromise = api.get(`/sensors/${sensor.sensor}`, {
          signal: controller.signal
        })
        .then(res => ({ 
          sensorName: sensor.sensor, 
          data: res.data, 
          unit: sensor.unit,
          error: null 
        }))
        .catch(err => ({ 
          sensorName: sensor.sensor, 
          data: null, 
          unit: sensor.unit,
          error: err.message 
        }))

        return Promise.race([fetchPromise, timeoutPromise])
          .catch(() => ({ 
            sensorName: sensor.sensor, 
            data: null, 
            unit: sensor.unit,
            error: 'Timeout' 
          }))
      })

      try {
        const results = await Promise.all(promises)
        
        const dataMap = {}
        const errorMap = {}
        
        results.forEach(result => {
          if (result.error) {
            errorMap[result.sensorName] = result.error
          } else {
            dataMap[result.sensorName] = { ...result.data, unit: result.unit }
          }
        })
        
        setSensorsData(dataMap)
        setErrors(errorMap)
      } catch (err) {
        console.error('Error in batch sensor loading:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAllSensors()

    let intervalId = null
    if (refreshInterval) {
      intervalId = setInterval(fetchAllSensors, refreshInterval)
    }

    return () => {
      controller.abort()
      if (intervalId) clearInterval(intervalId)
    }
  }, [sensors, refreshInterval])

  return { sensorsData, loading, errors }
}

// --------------------------------------------------
// Sistema de Toast Notifications
function useToast() {
  const [toasts, setToasts] = useState([])
  const timeoutsRef = useRef({})

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now() + Math.random()
    
    setToasts(prev => [...prev, { id, message, type }])
    
    timeoutsRef.current[id] = setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
      delete timeoutsRef.current[id]
    }, duration)
  }, [])

  const removeToast = useCallback((id) => {
    if (timeoutsRef.current[id]) {
      clearTimeout(timeoutsRef.current[id])
      delete timeoutsRef.current[id]
    }
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  useEffect(() => {
    return () => {
      Object.values(timeoutsRef.current).forEach(timeout => clearTimeout(timeout))
    }
  }, [])

  return { toasts, addToast, removeToast }
}

// --------------------------------------------------
// Árbol de jerarquía
const tree = {
  id: 'Escuela Superior Politécnica del Litoral (ESPOL)',
  label: 'Escuela Superior Politécnica del Litoral (ESPOL)',
  children: [
    {
      id: 'Facultad de Ingeniería en Electricidad y Computación (FIEC)',
      label: 'Facultad de Ingeniería en Electricidad y Computación (FIEC)',
      children: [
        {
          id: 'Edificio FIEC 11-C Laboratorios',
          label: 'Edificio FIEC 11-C Laboratorios',
          children: [
            {
              id: 'Edificio 11-C Piso 1',
              label: 'Edificio 11-C Piso 1',
              children: [
                { id: '11C-LabIoT', label: 'Laboratorio de IoT y Telemática', children: [] },
                { id: 'EST_MET', label: 'Jardín frontal del lab', children: [] }
              ]
            },
            {
              id: 'Edificio 11-C Piso 2',
              label: 'Edificio 11-C Piso 2',
              children: [
                { id: '11C-LabRDD', label: 'Laboratorio de Redes de Datos', children: [] },
                { id: '11C-LabSN', label: 'Laboratorio de Sistemas en la Nube', children: [] }
              ]
            }
          ]
        }
      ]
    }
  ]
}

const LAB_IDS = ['11C-LabIoT', 'EST_MET', '11C-LabRDD', '11C-LabSN']

// --------------------------------------------------
// Helpers
const findAllChildren = (nodeId, treeNode = tree) => {
  const children = []
  
  const traverse = (currentNode) => {
    if (currentNode.id === nodeId) {
      const collectChildren = (node) => {
        node.children.forEach(child => {
          children.push(child.id)
          collectChildren(child)
        })
      }
      collectChildren(currentNode)
      return true
    }
    
    for (const child of currentNode.children) {
      if (traverse(child)) return true
    }
    
    return false
  }
  
  traverse(treeNode)
  return children
}

const getLabPath = (labId) => {
  const basePath = [
    'Escuela Superior Politécnica del Litoral (ESPOL)',
    'Facultad de Ingeniería en Electricidad y Computación (FIEC)',
    'Edificio FIEC 11-C Laboratorios'
  ]
  
  if (labId === '11C-LabIoT' || labId === 'EST_MET') {
    basePath.push('Edificio 11-C Piso 1')
  } else if (labId === '11C-LabRDD' || labId === '11C-LabSN') {
    basePath.push('Edificio 11-C Piso 2')
  }
  
  return basePath
}

// --------------------------------------------------
// Función para categorizar sensores basado en su unidad
const categorizeSensor = (sensor) => {
  const unit = sensor.unit || null
  return UNIT_TO_CATEGORY[unit] || 'monitoring'
}

export default function FlowDiagram({ userRole = 'estudiante' }) {
  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [rfInstance, setRfInstance] = useState(null)
  
  // Control states
  const [expanded, setExpanded] = useState(new Set())
  const [activeLab, setActiveLab] = useState(null)
  const [activeEquip, setActiveEquip] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  
  // Nuevos estados para funcionalidades
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [activeFilters, setActiveFilters] = useState(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [chartModalSensor, setChartModalSensor] = useState(null)
  
  // ✅ NUEVO: Estado para el modal del Panel Admin
  const [showAdminModal, setShowAdminModal] = useState(false)
  
  // Toast notifications
  const { toasts, addToast, removeToast } = useToast()

  // API data
  const { equipments: labEquipments, error: labError } = useLabEquipments(activeLab)
  const { sensors, loading: sensorsLoading, error: sensorsError } = useEquipmentSensors(activeEquip)
  const { sensorsData, loading: sensorsDataLoading, errors: sensorErrors } = useMultipleSensorsData(
    sensors,
    30000
  )
  
  // Obtener todos los sensores de todos los equipos para filtrado
  const { allSensors: allLabSensors, loading: allSensorsLoading } = useAllEquipmentsSensors(labEquipments)

  // Fix definitivo para ResizeObserver
  useEffect(() => {
    // Suppress ResizeObserver errors
    const resizeObserverErrHandler = (e) => {
      if (e.message && e.message.includes('ResizeObserver loop')) {
        const resizeObserverErr = document.getElementById('webpack-dev-server-client-overlay');
        if(resizeObserverErr){
          resizeObserverErr.style.display = 'none';
        }
        return true;
      }
    };
    
    window.addEventListener('error', resizeObserverErrHandler);
    
    // Also override console.error temporarily
    const originalConsoleError = console.error;
    console.error = (...args) => {
      if (args[0]?.includes?.('ResizeObserver')) {
        return;
      }
      originalConsoleError.apply(console, args);
    };
    
    return () => {
      window.removeEventListener('error', resizeObserverErrHandler);
      console.error = originalConsoleError;
    };
  }, []);

  // Mostrar errores como toast
  useEffect(() => {
    if (labError) {
      addToast('Error cargando equipos del laboratorio', 'error', 4000)
    }
    if (sensorsError) {
      addToast('Error cargando sensores', 'error', 4000)
    }
    const errorCount = Object.keys(sensorErrors).length
    if (errorCount > 0) {
      addToast(`${errorCount} sensor(es) sin conexión`, 'warning', 3000)
    }
  }, [labError, sensorsError, sensorErrors, addToast])

  // Limpiar estados cuando se contraen nodos
  useEffect(() => {
    if (activeLab) {
      const labPath = getLabPath(activeLab)
      const shouldClearLab = labPath.some(nodeId => !expanded.has(nodeId))
      
      if (shouldClearLab) {
        setActiveLab(null)
        setActiveEquip(null)
      }
    }
    
    if (activeEquip && (!activeLab || !labEquipments.includes(activeEquip))) {
      setActiveEquip(null)
    }
  }, [expanded, activeLab, activeEquip, labEquipments])

  // Toggle Dark/Light mode con colores mejorados
  const toggleTheme = useCallback(() => {
    setIsDarkMode(prev => !prev)
    // Colores más suaves para el modo claro
    document.documentElement.style.setProperty('--bg-color', isDarkMode ? '#fef9f3' : '#0a0a0f')
    document.documentElement.style.setProperty('--text-color', isDarkMode ? '#374151' : 'rgb(243,244,246)')
    addToast(`Modo ${isDarkMode ? 'claro' : 'oscuro'} activado`, 'success', 2000)
  }, [isDarkMode, addToast])

  // Toggle filter
  const toggleFilter = useCallback((category) => {
    setActiveFilters(prev => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }, [])

  // ✅ NUEVO: Función para cerrar el modal del Panel Admin
  const handleCloseAdminModal = useCallback(() => {
    setShowAdminModal(false)
  }, [])

  // Función de búsqueda mejorada - busca en TODA la jerarquía
  const handleSearch = useCallback(async (query) => {
    if (!query) {
      addToast('Ingrese un nombre de sensor', 'warning', 2000)
      return
    }

    try {
      // Buscar en todos los laboratorios
      const allResults = await Promise.all(
        LAB_IDS.map(async (labId) => {
          try {
            // Obtener todos los sensores del laboratorio
            const sensorsRes = await api.get('/sensors/')
            
            const filterMap = {
              '11C-LabIoT': { db: '11C-LabIoT' },
              'EST_MET': { db_id: 'EST_MET' },
              '11C-LabRDD': { db: '11C-LabRDD' },
              '11C-LabSN': { db: '11C-LabSN' }
            }
            
            const filter = filterMap[labId]
            if (!filter) return null
            
            // Filtrar equipos del laboratorio
            const labEquipments = [...new Set(
              sensorsRes.data
                .filter(s => s.db === filter.db || s.db_id === filter.db_id)
                .map(s => s.equipment)
            )]
            
            // Buscar en cada equipo
            for (const equipment of labEquipments) {
              try {
                const eqRes = await api.get(`/equipment/${equipment}`)
                const foundSensor = eqRes.data.find(s => 
                  s.sensor.toLowerCase().includes(query.toLowerCase())
                )
                
                if (foundSensor) {
                  return {
                    labId,
                    equipment,
                    sensor: foundSensor,
                    found: true
                  }
                }
              } catch (err) {
                console.log(`Error checking equipment ${equipment}:`, err)
              }
            }
            
            return null
          } catch (err) {
            console.log(`Error searching in lab ${labId}:`, err)
            return null
          }
        })
      )
      
      const found = allResults.find(result => result && result.found)
      
      if (found) {
        // Construir la ruta completa
        const labPath = getLabPath(found.labId)
        
        // Expandir todos los nodos necesarios
        const newExpanded = new Set([...labPath, found.labId])
        setExpanded(newExpanded)
        
        // Activar el laboratorio y equipo
        setActiveLab(found.labId)
        
        // Esperar un poco para que se carguen los equipos
        setTimeout(() => {
          setActiveEquip(found.equipment)
          setSelectedNode(found.sensor.sensor)
          
          addToast(`Sensor "${found.sensor.sensor}" encontrado en ${found.equipment}`, 'success', 3000)
          
          // Centrar la vista después de otro delay
          setTimeout(() => {
            if (rfInstance) {
              const node = rfInstance.getNode(found.sensor.sensor)
              if (node && node.position) {
                rfInstance.setCenter(node.position.x, node.position.y, { 
                  zoom: 1, 
                  duration: 800 
                })
              }
            }
          }, 500)
        }, 500)
      } else {
        addToast(`No se encontró el sensor "${query}"`, 'error', 3000)
      }
    } catch (error) {
      console.error('Error en búsqueda:', error)
      addToast('Error al buscar el sensor', 'error', 3000)
    }
  }, [rfInstance, addToast, setExpanded, setActiveLab, setActiveEquip, setSelectedNode])

  // Función para abrir modal de gráfica de sensor
  const handleSensorChartClick = useCallback((sensor) => {
    setChartModalSensor(sensor)
    addToast(`Abriendo gráfica para ${sensor.sensor}`, 'info', 2000)
  }, [addToast])

  // ReactFlow Handlers
  const onInit = useCallback(flow => setRfInstance(flow), [])
  
  const onConnect = useCallback(params =>
    setEdges(es => addEdge({ ...params, type: 'animated' }, es)),
    [setEdges]
  )

  const onNodeClick = useCallback((_, node) => {
    // Nodos de control especiales
    if (node.id === 'theme-toggle') {
      toggleTheme()
      return
    }
    
    if (node.id === 'categories-control') {
      setShowFilters(prev => !prev)
      return
    }

    // ✅ MODIFICADO: Manejo del panel de administración
    if (node.id === 'admin-panel') {
      setShowAdminModal(true) // 🔄 CAMBIAR de addToast a abrir modal
      return
    }
    
    if (node.id.startsWith('category-')) {
      const category = node.id.replace('category-', '')
      toggleFilter(category)
      return
    }

    if (node.id === 'search-control') {
      return
    }

    // Comportamiento normal para nodos del árbol
    setSelectedNode(prevSelected => prevSelected === node.id ? null : node.id)
    
    setExpanded(prevExpanded => {
      const next = new Set(prevExpanded)
      
      if (next.has(node.id)) {
        next.delete(node.id)
        
        const allChildren = findAllChildren(node.id)
        allChildren.forEach(childId => next.delete(childId))
        
        if (node.id === activeLab || allChildren.includes(activeLab)) {
          setActiveLab(null)
          setActiveEquip(null)
        }
        if (node.id === activeEquip || allChildren.includes(activeEquip)) {
          setActiveEquip(null)
        }
      } else {
        next.add(node.id)
      }
      
      return next
    })

    if (labEquipments.includes(node.id)) {
      setActiveEquip(prev => prev === node.id ? null : node.id)
      if (activeEquip !== node.id) {
        addToast(`Equipo ${node.id} seleccionado`, 'info', 2000)
      }
    }
    else if (LAB_IDS.includes(node.id)) {
      setActiveLab(prev => prev === node.id ? null : node.id)
      if (activeLab !== node.id) {
        setActiveEquip(null)
        addToast(`Laboratorio activo: ${node.id}`, 'info', 2000)
      }
    }
    else if (expanded.has(node.id)) {
      const allChildren = findAllChildren(node.id)
      if (allChildren.includes(activeLab)) {
        setActiveLab(null)
        setActiveEquip(null)
      }
    }
  }, [labEquipments, activeLab, activeEquip, expanded, toggleTheme, toggleFilter, addToast, setShowAdminModal]) // ✅ AGREGADO: setShowAdminModal a dependencias

  // Funciones auxiliares
  const extractSensorValue = useCallback((sensorData) => {
    if (!sensorData) return null
    
    const excludeKeys = ['timestamp', 'metadata', 'id', 'sensor', 'equipment', 'db', 'db_id', 'unit']
    
    for (const [key, value] of Object.entries(sensorData)) {
      if (!excludeKeys.includes(key) && typeof value === 'number') {
        return { value, key }
      }
    }
    return null
  }, [])

  // Función para formatear números con decimales
  const formatNumber = useCallback((value) => {
    if (value === null || value === undefined || isNaN(value)) {
      return 'N/A'
    }
    
    if (Number.isInteger(value)) {
      return value.toString()
    }
    
    const str = value.toString()
    const parts = str.split('.')
    
    if (parts[1] && parts[1].length > 3) {
      return value.toFixed(3)
    }
    
    return value.toString()
  }, [])

  // Función mejorada para formatear timestamp a hora Ecuador (GMT-5)
  const formatTimestamp = useCallback((timestamp) => {
    if (!timestamp) return ''
    
    try {
      const date = new Date(timestamp)
      
      // Convertir a hora Ecuador (GMT-5)
      const ecuadorOffset = -5 * 60
      const localOffset = date.getTimezoneOffset()
      const diff = ecuadorOffset - localOffset
      
      const ecuadorDate = new Date(date.getTime() + diff * 60 * 1000)
      
      return ecuadorDate.toLocaleString('es-EC', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour12: false
      })
    } catch {
      return timestamp
    }
  }, [])

  const layoutConfig = useMemo(() => ({
    gapX: 500,
    gapY: 310,
    sensorsPerRow: 5,
    sensorSpacingX: 450,
    sensorSpacingY: 210,
    sensorOffsetX: 900,
    sensorOffsetY: 1.2
  }), [])

  // Filtrar equipos basado en categorías activas
  const getFilteredEquipments = useCallback(() => {
    if (activeFilters.size === 0 || !allLabSensors) {
      return labEquipments
    }

    return labEquipments.filter(equipment => {
      const sensors = allLabSensors[equipment] || []
      return sensors.some(sensor => {
        const category = categorizeSensor(sensor)
        return activeFilters.has(category)
      })
    })
  }, [labEquipments, allLabSensors, activeFilters])

  // Renderizado de nodos y aristas
  useEffect(() => {
    const allNodes = []
    const allEdges = []
    const positions = {}
    const { gapX, gapY, sensorsPerRow, sensorSpacingX, sensorSpacingY, sensorOffsetX, sensorOffsetY } = layoutConfig

    // 1) Nodos de control con mejor espaciado
    // Buscar sensor primero
    allNodes.push({
      id: 'search-control',
      type: 'search',
      data: { 
        isDarkMode,
        onSearch: handleSearch
      },
      position: { x: 50, y: 50 },
      draggable: false
    })

    // Modo claro/oscuro con más espacio (70px gap)
    allNodes.push({
      id: 'theme-toggle',
      type: 'control',
      data: { 
        icon: isDarkMode ? '🌞' : '🌙',
        label: isDarkMode ? 'Modo Claro' : 'Modo Oscuro',
        isDarkMode
      },
      position: { x: 50, y: 160 }, // Aumentado de 140 a 160 para más espacio
      draggable: false
    })

    // Categorías con espacio consistente
    allNodes.push({
      id: 'categories-control',
      type: 'control',
      data: { 
        icon: '📊',
        label: 'Categorías',
        isDarkMode
      },
      position: { x: 50, y: 230 },
      draggable: false
    })

    // ✅ NUEVO: Panel de administración para profesores
    if (userRole === 'profesor') {
      allNodes.push({
        id: 'admin-panel',
        type: 'control',
        data: { 
          icon: '⚙️',
          label: 'Panel Admin',
          isDarkMode,
          isAdminPanel: true
        },
        position: { x: 50, y: 300 },
        draggable: false
      })
    }

    // Mostrar opciones de categorías si está activo
    if (showFilters) {
      const categories = Object.keys(CATEGORY_NAMES)
      const startY = userRole === 'profesor' ? 380 : 310 // Ajustar posición según rol
      categories.forEach((category, i) => {
        allNodes.push({
          id: `category-${category}`,
          type: 'control',
          data: { 
            icon: activeFilters.has(category) ? '✅' : '⬜',
            label: CATEGORY_NAMES[category],
            isDarkMode,
            isActive: activeFilters.has(category),
            categoryColor: CATEGORY_COLORS[category]
          },
          position: { x: 50, y: startY + i * 60 },
          draggable: false
        })
      })
    }

    // 2) Construir árbol principal
    function walk(n, depth, parent) {
      const x = depth * gapX + 300
      let y
      
      if (!parent) {
        y = gapY
      } else if (depth <= 2) {
        y = positions[parent.id].y + gapY * 0.2
      } else {
        const siblings = parent.children
        const index = siblings.findIndex(c => c.id === n.id)
        const offset = gapY * (depth === 3 ? 1.8 : 1.2)
        y = positions[parent.id].y + (index === 0 ? -offset : offset)
      }
      
      positions[n.id] = { x, y }
      
      const isSelected = selectedNode === n.id
      const nodeIcon = NODE_ICONS[n.label] || NODE_ICONS['default']
      
      allNodes.push({
        id: n.id,
        type: 'turbo',
        data: { 
          title: n.label,
          isSelected,
          isDarkMode,
          icon: nodeIcon,
          showIconInCloud: true // Mostrar icono en la nube, no dentro
        },
        position: { x, y },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        selected: isSelected
      })
      
      if (parent) {
        allEdges.push({
          id: `${parent.id}-${n.id}`,
          source: parent.id,
          target: n.id,
          type: 'animated',
          animated: selectedNode === parent.id || selectedNode === n.id
        })
      }

      if (expanded.has(n.id)) {
        n.children.forEach(c => walk(c, depth + 1, n))
      }
    }
    
    walk(tree, 0, null)

    // 3) Renderizar equipos del laboratorio activo (filtrados por categoría)
    if (activeLab && labEquipments.length) {
      const labPos = positions[activeLab]
      const filteredEquipments = getFilteredEquipments()
      
      if (labPos) { // Validar que labPos existe
        filteredEquipments.forEach((eq, i) => {
          const x = labPos.x + (i + 1) * gapX * 0.9
          const y = labPos.y - gapY * 1
          positions[eq] = { x, y }
          
          const isSelected = selectedNode === eq
          
          allNodes.push({
            id: eq,
            type: 'turbo',
            data: { 
              title: eq,
              subtitle: 'Equipo IoT',
              isSelected,
              isDarkMode,
              icon: '📟',
              showIconInCloud: true
            },
            position: { x, y },
            sourcePosition: Position.Bottom,
            targetPosition: Position.Top,
            selected: isSelected
          })
          
          allEdges.push({
            id: `${eq}-${activeLab}`,
            source: eq,
            target: activeLab,
            type: 'animated',
            animated: selectedNode === eq || selectedNode === activeLab
          })
        })
      }
    }

    // 4) Renderizar sensores del equipo activo en grid
    if (activeEquip && sensors.length && !sensorsLoading) {
      const equipPos = positions[activeEquip]
      
      if (equipPos) { // Validar que equipPos existe
        // Filtrar sensores según categorías activas
        let filteredSensors = sensors
        if (activeFilters.size > 0) {
          filteredSensors = sensors.filter(sensor => {
            const category = categorizeSensor(sensor)
            return activeFilters.has(category)
          })
        }
        
        filteredSensors.forEach((sensor, i) => {
          const sensorData = sensorsData[sensor.sensor]
          const sensorValueInfo = extractSensorValue(sensorData)
          const category = categorizeSensor(sensor)
          
          const col = i % sensorsPerRow
          const row = Math.floor(i / sensorsPerRow)
          
          const totalWidth = (sensorsPerRow - 1) * sensorSpacingX
          const startX = equipPos.x - totalWidth / 2 + sensorOffsetX
          
          const x = startX + col * sensorSpacingX
          const y = equipPos.y - gapY * sensorOffsetY - row * sensorSpacingY
          
          positions[sensor.sensor] = { x, y }
          
          let sensorTitle = sensor.sensor
          let sensorSubtitle = ''
          let sensorFooter = ''
          
          if (sensorData) {
            const timestamp = formatTimestamp(sensorData.timestamp)
            const rawValue = sensorValueInfo?.value
            const value = formatNumber(rawValue)
            const unit = sensor.unit || ''
            
            sensorSubtitle = timestamp
            sensorFooter = `${value} ${unit}`.trim()
            
            if (sensorErrors[sensor.sensor]) {
              sensorSubtitle = '⚠️ Error de conexión'
              sensorFooter = 'Sin datos'
            }
          } else if (sensorsDataLoading) {
            sensorSubtitle = 'Cargando...'
            sensorFooter = '...'
          } else {
            sensorSubtitle = 'Sin conexión'
            sensorFooter = '--'
          }
          
          const isSelected = selectedNode === sensor.sensor
          
          // Icono según categoría
          const categoryIcons = {
            power: '⚡',
            electrical: '🔌',
            temperature: '🌡️',
            humidity: '💧',
            pressure: '🎯',
            air_quality: '💨',
            weather: '🌤️',
            monitoring: '📊'
          }
          
          allNodes.push({
            id: sensor.sensor,
            type: 'turbo',
            data: { 
              title: sensorTitle,
              subtitle: sensorSubtitle,
              footer: sensorFooter,
              isSelected,
              isDarkMode,
              category,
              categoryColor: CATEGORY_COLORS[category],
              icon: categoryIcons[category] || '📡',
              showIconInCloud: false, // Para sensores, mostrar icono de gráfica en la nube
              isSensor: true, // Marcar como sensor
              onChartClick: () => handleSensorChartClick(sensor) // Función para abrir modal
            },
            position: { x, y },
            sourcePosition: Position.Bottom,
            targetPosition: Position.Top,
            selected: isSelected
          })
          
          allEdges.push({
            id: `${sensor.sensor}-${activeEquip}`,
            source: sensor.sensor,
            target: activeEquip,
            type: 'animated',
            animated: selectedNode === sensor.sensor || selectedNode === activeEquip
          })
        })
      }
    }

    setNodes(allNodes)
    setEdges(allEdges)
    
    // Debounce fitView para evitar problemas de ResizeObserver
    if (rfInstance && (allNodes.length > nodes.length + 5 || allNodes.length < nodes.length - 5)) {
      const timer = setTimeout(() => {
        try {
          rfInstance.fitView({ padding: 0.2, duration: 800 })
        } catch (err) {
          console.warn('FitView error:', err)
        }
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [
    expanded, 
    activeLab, 
    labEquipments, 
    activeEquip, 
    sensors, 
    sensorsData, 
    sensorsLoading,
    sensorsDataLoading,
    sensorErrors,
    selectedNode,
    isDarkMode,
    activeFilters,
    showFilters,
    allLabSensors,
    userRole,
    setNodes, 
    setEdges, 
    rfInstance,
    nodes.length,
    layoutConfig,
    extractSensorValue,
    formatTimestamp,
    formatNumber,
    getFilteredEquipments,
    handleSearch,
    handleSensorChartClick
  ])

  return (
    <ReactFlowProvider>
      <div style={{ 
        width: '100%', 
        height: '100vh',
        position: 'relative'
      }}>
        <BackgroundGradient isDarkMode={isDarkMode} />
        
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          defaultEdgeOptions={{ 
            type: 'animated', 
            markerEnd: 'url(#edge-circle)' 
          }}
          onInit={onInit}
          onNodeClick={onNodeClick}
          onConnect={onConnect}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.1}
          maxZoom={2}
          defaultViewport={{ x: 0, y: 0, zoom: 0.5 }}
          style={{ 
            background: isDarkMode 
              ? 'radial-gradient(ellipse at center, #1a0f2e 0%, #0a0a0f 100%)' 
              : 'transparent'
          }}
          proOptions={{ hideAttribution: true }}
        >
          <MiniMap 
            nodeColor={n => {
              if (n.id.startsWith('category-') || n.id === 'theme-toggle' || n.id === 'categories-control' || n.id === 'search-control') {
                return '#9333ea'
              }
              return n.selected ? '#e92a67' : '#95679e'
            }}
            maskColor="rgba(0,0,0,0.2)" 
            style={{ 
              background: isDarkMode ? '#1a0f2e' : '#fef9f3',
              border: `1px solid ${isDarkMode ? '#e92a67' : '#667eea'}30`
            }} 
          />
          <Controls 
            style={{ 
              background: isDarkMode ? '#1a0f2e' : '#fef9f3',
              border: `1px solid ${isDarkMode ? '#e92a67' : '#667eea'}30`
            }}
          />
          <Background 
            color={isDarkMode ? "#2a1f4a" : "#e8d5c4"} 
            gap={16} 
            variant="dots"
          />
          
          {/* SVG Definitions para gradientes y marcadores */}
          <svg style={{ position: 'absolute', width: 0, height: 0 }}>
            <defs>
              <linearGradient id="edge-gradient">
                <stop offset="0%" stopColor="#e92a67" />
                <stop offset="50%" stopColor="#a853ba" />
                <stop offset="100%" stopColor="#2a8af6" />
              </linearGradient>
              <marker
                id="edge-circle"
                viewBox="-5 -5 10 10"
                refX="0"
                refY="0"
                markerUnits="strokeWidth"
                markerWidth="10"
                markerHeight="10"
                orient="auto"
              >
                <circle r="3" fill="url(#edge-gradient)" />
              </marker>
            </defs>
          </svg>
        </ReactFlow>
        
        {/* Toast Container */}
        <Toast toasts={toasts} onRemove={removeToast} />
        
        {/* Chart Modal */}
        {chartModalSensor && (
          <ChartModal
            sensor={chartModalSensor}
            onClose={() => setChartModalSensor(null)}
            isDarkMode={isDarkMode}
          />
        )}
        
        {/* ✅ NUEVO: Modal del Panel de Administración */}
        <AdminPanelModal 
          isOpen={showAdminModal}
          onClose={handleCloseAdminModal}
          addToast={addToast}
        />
      </div>
    </ReactFlowProvider>
  )
}