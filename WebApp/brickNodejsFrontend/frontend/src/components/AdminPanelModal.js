// src/components/AdminPanelModal.js

import React, { useState, useEffect } from 'react';

const AdminPanelModal = ({ isOpen, onClose, addToast }) => {
  // Estados básicos
  const [entityName, setEntityName] = useState('');
  const [baseClass, setBaseClass] = useState('');
  const [entityClass, setEntityClass] = useState('');
  const [selectedProperties, setSelectedProperties] = useState([]);
  const [propertyValues, setPropertyValues] = useState({});
  
  // Estados para datos de APIs
  const [entityClasses, setEntityClasses] = useState([]);
  const [classProperties, setClassProperties] = useState({});
  const [existingInstances, setExistingInstances] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Estados para propiedades con instancias
  const [propertyInstances, setPropertyInstances] = useState({});
  const [loadingPropertyInstances, setLoadingPropertyInstances] = useState({});

  // Estados para gestión de entidades
  const [creatingEntity, setCreatingEntity] = useState(false);
  const [deletingEntity, setDeletingEntity] = useState('');

  // Clases base disponibles
  const BASE_CLASSES = [
    { value: 'brick:Entity', label: 'brick:Entity', type: 'brick' },
    { value: 'rec:Agent', label: 'rec:Agent', type: 'rec' },
    { value: 'rec:Asset', label: 'rec:Asset', type: 'rec' },
    { value: 'rec:BuildingElement', label: 'rec:BuildingElement', type: 'rec' },
    { value: 'rec:Collection', label: 'rec:Collection', type: 'rec' },
    { value: 'rec:Event', label: 'rec:Event', type: 'rec' },
    { value: 'rec:Information', label: 'rec:Information', type: 'rec' },
    { value: 'rec:Space', label: 'rec:Space', type: 'rec' }
  ];

  const cleanOptionText = (text) => {
    if (!text || typeof text !== 'string') return text;
    return text.replace(/^[a-zA-Z_]+:/, '').trim();
  };

  const getDisplayName = (fullName) => {
    if (!fullName) return fullName;
    return cleanOptionText(fullName);
  };

  // Effect para cargar clases cuando cambia baseClass
  useEffect(() => {
    console.log('🔥 useEffect triggered, baseClass:', baseClass);
    
    if (!baseClass) {
      console.log('❌ No baseClass, clearing entityClasses');
      setEntityClasses([]);
      return;
    }

    console.log('✅ Loading classes for:', baseClass);
    loadEntityClasses(baseClass);
  }, [baseClass]);

  // Effect para cargar propiedades cuando cambia entityClass
  useEffect(() => {
    console.log('🔥 useEffect triggered, entityClass:', entityClass);
    
    if (!entityClass) {
      console.log('❌ No entityClass, clearing data');
      setClassProperties({});
      return;
    }

    console.log('✅ Loading properties for:', entityClass);
    loadClassProperties(entityClass);
  }, [entityClass]);

  // Función simplificada para cargar clases de entidad
  const loadEntityClasses = async (baseClassValue) => {
    console.log('🚀 loadEntityClasses called with:', baseClassValue);
    
    setLoading(true);
    setEntityClasses([]); // Limpiar primero
    
    try {
      const url = `http://localhost:8000/api/getAllSubClasses/${encodeURIComponent(baseClassValue)}`;
      console.log('📡 Fetching URL:', url);
      
      const response = await fetch(url);
      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📦 Raw data received:', data);
      console.log('📦 Data type:', typeof data);
      
      let classes = [];
      
      if (data && data.entities && Array.isArray(data.entities)) {
        classes = data.entities;
        console.log('✅ Found entities in data.entities:', classes.length);
      } else {
        console.log('❌ No entities found in expected structure');
      }
      
      console.log('🎯 Setting entityClasses to:', classes);
      setEntityClasses(classes);
      
      if (classes.length > 0) {
        addToast(`✅ ${classes.length} clases cargadas para ${baseClassValue}`, 'success', 3000);
      } else {
        addToast(`⚠️ No se encontraron clases para ${baseClassValue}`, 'warning', 3000);
      }
      
    } catch (error) {
      console.error('❌ Error in loadEntityClasses:', error);
      addToast(`❌ Error: ${error.message}`, 'error', 4000);
      setEntityClasses([]);
    } finally {
      setLoading(false);
    }
  };

  // Función para cargar propiedades de clase
  const loadClassProperties = async (classValue) => {
    console.log('🚀 loadClassProperties called with:', classValue);
    
    try {
      const url = `http://localhost:8000/api/getClassProperties/${encodeURIComponent(classValue)}`;
      console.log('📡 Fetching properties URL:', url);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📦 Properties data received:', data);
      
      if (data && typeof data === 'object') {
        setClassProperties(data);
        const count = Object.keys(data).length;
        addToast(`✅ ${count} propiedades cargadas`, 'success', 2000);
      } else {
        setClassProperties({});
        addToast(`⚠️ No se encontraron propiedades`, 'warning', 2000);
      }
      
    } catch (error) {
      console.error('❌ Error in loadClassProperties:', error);
      addToast(`❌ Error cargando propiedades: ${error.message}`, 'error', 4000);
      setClassProperties({});
    }
  };

  // Función para cargar instancias de una propiedad específica
  const loadPropertyInstances = async (propertyType) => {
    console.log('🚀 loadPropertyInstances called with:', propertyType);
    
    // Si ya está cargando o ya tiene datos, no cargar de nuevo
    if (loadingPropertyInstances[propertyType] || propertyInstances[propertyType]) {
      return;
    }
    
    setLoadingPropertyInstances(prev => ({ ...prev, [propertyType]: true }));
    
    try {
      const url = `http://localhost:8000/api/getInstances/${encodeURIComponent(propertyType)}`;
      console.log('📡 Fetching property instances URL:', url);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📦 Property instances data received:', data);
      
      let instances = [];
      
      if (data && data.targets && Array.isArray(data.targets)) {
        instances = data.targets;
      } else if (Array.isArray(data)) {
        instances = data;
      }
      
      setPropertyInstances(prev => ({ ...prev, [propertyType]: instances }));
      
    } catch (error) {
      console.error('❌ Error in loadPropertyInstances:', error);
      setPropertyInstances(prev => ({ ...prev, [propertyType]: [] }));
    } finally {
      setLoadingPropertyInstances(prev => ({ ...prev, [propertyType]: false }));
    }
  };

  // Función para crear/insertar nueva entidad
  const createEntity = async () => {
    console.log('🚀 createEntity called');
    
    // Validaciones básicas
    if (!entityName.trim()) {
      addToast('❌ El nombre de la entidad es requerido', 'error', 3000);
      return;
    }
    
    if (!entityClass) {
      addToast('❌ Debe seleccionar una clase de entidad', 'error', 3000);
      return;
    }

    if (selectedProperties.length === 0) {
      addToast('❌ Debe seleccionar al menos una propiedad', 'error', 3000);
      return;
    }

    // Solo verificar propiedades configurables
    const configurableProperties = getConfigurableProperties();
    const propertiesWithValues = configurableProperties.filter(prop => propertyValues[prop]);
    
    if (configurableProperties.length === 0) {
      addToast('❌ No hay propiedades configurables disponibles', 'error', 4000);
      return;
    }
    
    if (propertiesWithValues.length === 0) {
      addToast('❌ Debe configurar al menos una propiedad de las disponibles', 'error', 4000);
      return;
    }

    // Mostrar información sobre propiedades omitidas
    const missingConfigurableValues = configurableProperties.filter(prop => !propertyValues[prop]);
    if (missingConfigurableValues.length > 0) {
      addToast(`⚠️ Se omitirán propiedades configurables sin valor: ${missingConfigurableValues.join(', ')}`, 'warning', 4000);
    }
    
    const nonConfigurableProperties = selectedProperties.filter(propName => {
      const propType = classProperties[propName];
      return !isPropertyConfigurable(propName, propType);
    });
    if (nonConfigurableProperties.length > 0) {
      addToast(`ℹ️ Propiedades sin opciones disponibles (omitidas): ${nonConfigurableProperties.join(', ')}`, 'info', 4000);
    }

    setCreatingEntity(true);
    
    try {
      // Preparar datos para enviar
      const entityData = {
        name: entityName.trim(),
        baseClass: baseClass,
        entityClass: entityClass,
        properties: {}
      };

      // Añadir solo las propiedades configurables que tienen valores
      const configurableProperties = getConfigurableProperties();
      configurableProperties.forEach(prop => {
        if (propertyValues[prop]) {
          entityData.properties[prop] = propertyValues[prop];
        }
      });

      console.log('📦 Sending entity data:', entityData);
      console.log('📊 Property stats:', {
        totalSelected: selectedProperties.length,
        configurable: configurableProperties.length,
        configured: propertiesWithValues.length,
        nonConfigurable: selectedProperties.length - configurableProperties.length
      });

      const response = await fetch('http://localhost:8000/api/insertData/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entityData)
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorData}`);
      }

      const result = await response.json();
      console.log('✅ Entity created successfully:', result);

      // Limpiar formulario
      setEntityName('');
      setBaseClass('');
      setEntityClass('');
      setSelectedProperties([]);
      setPropertyValues({});
      setEntityClasses([]);
      setClassProperties({});

      addToast('🎉 Entidad creada exitosamente', 'success', 4000);
      
      // Opcional: cerrar modal después de crear
      // onClose();
      
    } catch (error) {
      console.error('❌ Error creating entity:', error);
      addToast(`❌ Error al crear entidad: ${error.message}`, 'error', 5000);
    } finally {
      setCreatingEntity(false);
    }
  };

  // Función para eliminar entidad
  const deleteEntity = async (entityName) => {
    console.log('🚀 deleteEntity called with:', entityName);
    
    if (!entityName.trim()) {
      addToast('❌ Nombre de entidad requerido para eliminar', 'error', 3000);
      return;
    }

    const confirmDelete = window.confirm(`¿Está seguro de eliminar la entidad "${entityName}"?`);
    if (!confirmDelete) {
      return;
    }

    setDeletingEntity(entityName);
    
    try {
      const response = await fetch(`http://localhost:8000/api/deleteData/${encodeURIComponent(entityName)}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorData}`);
      }

      const result = await response.json();
      console.log('✅ Entity deleted successfully:', result);

      addToast(`🗑️ Entidad "${entityName}" eliminada exitosamente`, 'success', 4000);
      
    } catch (error) {
      console.error('❌ Error deleting entity:', error);
      addToast(`❌ Error al eliminar entidad: ${error.message}`, 'error', 5000);
    } finally {
      setDeletingEntity('');
    }
  };

  // Función para verificar si un tipo es primitivo
  const isPrimitiveType = (type) => {
    const primitiveTypes = ['string', 'boolean', 'int', 'float', 'date', 'datetime'];
    return primitiveTypes.some(primitive => type.toLowerCase().includes(primitive));
  };

  // Función para verificar si una propiedad es configurable (ARREGLADO)
  const isPropertyConfigurable = (propertyName, propertyType) => {
    // Los tipos primitivos siempre son configurables
    if (isPrimitiveType(propertyType)) {
      return true;
    }
    
    // Para tipos complejos, verificar si hay instancias disponibles
    // BUGFIX: No usar propertyInstances[propertyType] directamente porque puede estar undefined
    // durante la carga inicial. En su lugar, ser más permisivo y permitir que se seleccione
    // la propiedad para que pueda cargar las instancias
    const instances = propertyInstances[propertyType];
    const isLoading = loadingPropertyInstances[propertyType];
    
    // Si está cargando o no hemos intentado cargar todavía, considerarla configurable
    if (isLoading || instances === undefined) {
      return true;
    }
    
    // Solo considerarla no configurable si definitivamente no hay instancias
    return instances && instances.length > 0;
  };

  // Obtener solo las propiedades configurables
  const getConfigurableProperties = () => {
    return selectedProperties.filter(propName => {
      const propType = classProperties[propName];
      return isPropertyConfigurable(propName, propType);
    });
  };

  // Función para manejar selección de propiedades
  const handlePropertySelection = (propertyName) => {
    setSelectedProperties(prev => {
      if (prev.includes(propertyName)) {
        // Remover propiedad
        const newSelected = prev.filter(p => p !== propertyName);
        setPropertyValues(prevValues => {
          const newValues = { ...prevValues };
          delete newValues[propertyName];
          return newValues;
        });
        return newSelected;
      } else {
        // Añadir propiedad
        const propertyType = classProperties[propertyName];
        
        // Si no es primitivo, cargar instancias
        if (!isPrimitiveType(propertyType)) {
          loadPropertyInstances(propertyType);
        }
        
        return [...prev, propertyName];
      }
    });
  };

  // Función para renderizar input según tipo de propiedad
  const renderPropertyInput = (propertyName, propertyType) => {
    const isSelected = selectedProperties.includes(propertyName);
    
    if (!isSelected) return null;

    // Para tipos primitivos
    if (isPrimitiveType(propertyType)) {
      let inputType = 'text';
      
      if (propertyType.toLowerCase().includes('boolean')) {
        return (
          <select
            value={propertyValues[propertyName] || ''}
            onChange={(e) => setPropertyValues(prev => ({ ...prev, [propertyName]: e.target.value }))}
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: '6px',
              border: '1px solid #444',
              background: '#2a2a2a',
              color: '#fff',
              fontSize: '14px',
              boxSizing: 'border-box'
            }}
          >
            <option value="">Seleccionar...</option>
            <option value="true">True</option>
            <option value="false">False</option>
          </select>
        );
      }
      
      if (propertyType.toLowerCase().includes('int') || propertyType.toLowerCase().includes('float')) {
        inputType = 'number';
      } else if (propertyType.toLowerCase().includes('date')) {
        inputType = 'date';
      }

      return (
        <input
          type={inputType}
          value={propertyValues[propertyName] || ''}
          onChange={(e) => setPropertyValues(prev => ({ ...prev, [propertyName]: e.target.value }))}
          placeholder={`Ingrese ${propertyName}...`}
          style={{
            width: '100%',
            padding: '12px 16px',
            borderRadius: '6px',
            border: '1px solid #444',
            background: '#2a2a2a',
            color: '#fff',
            fontSize: '14px',
            boxSizing: 'border-box'
          }}
        />
      );
    }

    // Para tipos con instancias
    const instances = propertyInstances[propertyType] || [];
    const isLoading = loadingPropertyInstances[propertyType];

    return (
      <select
        value={propertyValues[propertyName] || ''}
        onChange={(e) => setPropertyValues(prev => ({ ...prev, [propertyName]: e.target.value }))}
        style={{
          width: '100%',
          padding: '12px 16px',
          borderRadius: '6px',
          border: '1px solid #444',
          background: '#2a2a2a',
          color: '#fff',
          fontSize: '14px',
          boxSizing: 'border-box'
        }}
      >
        <option value="">
          {isLoading ? 'Cargando...' : 'Seleccionar instancia...'}
        </option>
        {instances.map((instance, idx) => (
          <option key={idx} value={instance}>
            {getDisplayName(instance)}
          </option>
        ))}
      </select>
    );
  };

  if (!isOpen) return null;

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
        background: 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)',
        borderRadius: '20px',
        padding: '0',
        maxWidth: '95vw',
        maxHeight: '95vh',
        width: '1400px',
        height: '800px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        border: '1px solid #444'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 30px',
          borderBottom: '1px solid #444',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px' }}>⚙️</span>
            <h2 style={{ 
              margin: 0, 
              color: '#fff', 
              fontSize: '24px',
              fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif"
            }}>
              Panel de Administración
            </h2>
            <span style={{
              background: 'rgba(255,255,255,0.2)',
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#fff'
            }}>
              Gestión de Entidades IoT
            </span>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#ef4444',
              color: '#fff',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.background = '#dc2626'}
            onMouseLeave={(e) => e.target.style.background = '#ef4444'}
          >
            ✕ Cerrar
          </button>
        </div>

        {/* Content */}
        <div style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: '20px',
          padding: '20px',
          overflow: 'auto'
        }}>
          {/* Columna 1: Crear Nueva Entidad */}
          <div style={{
            background: '#242424',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid #444'
          }}>
            <h3 style={{
              color: '#f59e0b',
              margin: '0 0 20px 0',
              fontSize: '18px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              🏗️ Crear Nueva Entidad
            </h3>

            {/* Nombre de la entidad */}
            <div style={{ marginBottom: '16px', padding: '0 4px' }}>
              <label style={{
                display: 'block',
                color: '#e5e7eb',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                🏷️ Nombre de la entidad:
              </label>
              <input
                type="text"
                value={entityName}
                onChange={(e) => setEntityName(e.target.value)}
                placeholder="Ej: lab electronica"
                style={{
                  width: '100%',
                  padding: '14px 18px',
                  borderRadius: '8px',
                  border: '1px solid #444',
                  background: '#1a1a1a',
                  color: '#fff',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            {/* Clase Base */}
            <div style={{ marginBottom: '16px', padding: '0 4px' }}>
              <label style={{
                display: 'block',
                color: '#f59e0b',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                🔧 1. Clase Base:
              </label>
              <select
                value={baseClass}
                onChange={(e) => setBaseClass(e.target.value)}
                style={{
                  width: '100%',
                  padding: '14px 18px',
                  borderRadius: '8px',
                  border: '1px solid #444',
                  background: '#1a1a1a',
                  color: '#fff',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
              >
                <option value="">Seleccionar clase base...</option>
                {BASE_CLASSES.map(cls => (
                  <option key={cls.value} value={cls.value}>
                    {getDisplayName(cls.label)}
                  </option>
                ))}
              </select>
            </div>

            {/* Clase Entidad */}
            <div style={{ marginBottom: '16px', padding: '0 4px' }}>
              <label style={{
                display: 'block',
                color: '#8b5cf6',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                🏗️ 2. Clase Entidad: {entityClasses.length > 0 && `(${entityClasses.length} disponibles)`}
              </label>
              <select
                value={entityClass}
                onChange={(e) => setEntityClass(e.target.value)}
                disabled={!baseClass || loading}
                style={{
                  width: '100%',
                  padding: '14px 18px',
                  borderRadius: '8px',
                  border: '1px solid #444',
                  background: loading ? '#333' : '#1a1a1a',
                  color: '#fff',
                  fontSize: '14px',
                  boxSizing: 'border-box',
                  opacity: (!baseClass || loading) ? 0.5 : 1
                }}
              >
                <option value="">
                  {loading ? 'Cargando...' : 'Seleccionar clase entidad...'}
                </option>
                {entityClasses.map((cls, idx) => (
                  <option key={idx} value={cls}>
                    {getDisplayName(cls)}
                  </option>
                ))}
              </select>
              {loading && (
                <div style={{ color: '#6b7280', fontSize: '12px', marginTop: '4px' }}>
                  Debug: {entityClasses.length} clases • Loading: {loading.toString()}
                </div>
              )}
            </div>

            {/* Propiedades */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                color: '#10b981',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                ⚡ 3. Propiedades {Object.keys(classProperties).length > 0 && `(${Object.keys(classProperties).length} disponibles)`}:
              </label>
              
              {/* Indicador de progreso */}
              {selectedProperties.length > 0 && (
                <div style={{
                  background: '#1a1a1a',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  marginBottom: '8px',
                  fontSize: '12px'
                }}>
                  <div style={{ color: '#10b981', marginBottom: '2px' }}>
                    📊 {(() => {
                      const configurableProps = getConfigurableProperties();
                      const configuredProps = configurableProps.filter(prop => propertyValues[prop]);
                      return `${configuredProps.length} de ${configurableProps.length} propiedades configurables completadas`;
                    })()}
                  </div>
                  {(() => {
                    const nonConfigurableCount = selectedProperties.length - getConfigurableProperties().length;
                    if (nonConfigurableCount > 0) {
                      return (
                        <div style={{ color: '#6b7280', fontSize: '11px' }}>
                          ℹ️ {nonConfigurableCount} propiedades sin opciones disponibles (se omitirán)
                        </div>
                      );
                    }
                    return null;
                  })()}
                </div>
              )}
              
              <div style={{
                maxHeight: '200px',
                overflowY: 'auto',
                border: '1px solid #444',
                borderRadius: '8px',
                background: '#1a1a1a'
              }}>
                {Object.entries(classProperties).map(([propName, propType]) => {
                  const isConfigurable = isPropertyConfigurable(propName, propType);
                  const isSelected = selectedProperties.includes(propName);
                  
                  return (
                    <div key={propName} style={{
                      padding: '8px 12px',
                      borderBottom: '1px solid #333',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      opacity: isConfigurable ? 1 : 0.6
                    }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ 
                          color: '#fff', 
                          fontSize: '14px', 
                          fontWeight: '600',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}>
                          {propName}
                          {!isConfigurable && <span style={{ fontSize: '12px', color: '#f59e0b' }}>⚠️</span>}
                        </div>
                        <div style={{ color: '#6b7280', fontSize: '12px' }}>
                          {propType}
                          {!isConfigurable && !isPrimitiveType(propType) && 
                            <span style={{ color: '#f59e0b' }}> (Sin instancias disponibles)</span>
                          }
                        </div>
                      </div>
                      <button
                        onClick={() => handlePropertySelection(propName)}
                        style={{
                          background: isSelected ? '#10b981' : 'transparent',
                          color: isSelected ? '#fff' : '#10b981',
                          border: '2px solid #10b981',
                          borderRadius: '6px',
                          padding: '4px 8px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          fontWeight: '600',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        {isSelected ? '✓' : '+'}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Botón Crear */}
            <button
              onClick={createEntity}
              disabled={(() => {
                if (!entityName || !entityClass || selectedProperties.length === 0 || creatingEntity) return true;
                const configurableProps = getConfigurableProperties();
                return configurableProps.length === 0 || configurableProps.filter(prop => propertyValues[prop]).length === 0;
              })()}
              style={{
                width: '100%',
                padding: '12px',
                background: (() => {
                  if (creatingEntity) return '#6b7280';
                  if (!entityName || !entityClass || selectedProperties.length === 0) return '#6b7280';
                  const configurableProps = getConfigurableProperties();
                  if (configurableProps.length === 0 || configurableProps.filter(prop => propertyValues[prop]).length === 0) return '#6b7280';
                  return 'linear-gradient(135deg, #8b5cf6 0%, #667eea 100%)';
                })(),
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: (() => {
                  if (creatingEntity) return 'not-allowed';
                  if (!entityName || !entityClass || selectedProperties.length === 0) return 'not-allowed';
                  const configurableProps = getConfigurableProperties();
                  if (configurableProps.length === 0 || configurableProps.filter(prop => propertyValues[prop]).length === 0) return 'not-allowed';
                  return 'pointer';
                })(),
                transition: 'all 0.2s ease'
              }}
            >
              {creatingEntity ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid transparent',
                    borderTop: '2px solid white',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                  Creando Entidad...
                </div>
              ) : (
                '🚀 Crear Entidad'
              )}
            </button>
            
            {/* Texto de ayuda */}
            <div style={{
              fontSize: '12px',
              color: '#6b7280',
              textAlign: 'center',
              marginTop: '8px'
            }}>
              {!entityName ? '📝 Ingrese el nombre de la entidad' :
               !entityClass ? '🏗️ Seleccione una clase de entidad' :
               selectedProperties.length === 0 ? '⚡ Seleccione al menos una propiedad' :
               (() => {
                 const configurableProps = getConfigurableProperties();
                 const configuredProps = configurableProps.filter(prop => propertyValues[prop]);
                 return configurableProps.length === 0 ? '❌ No hay propiedades configurables disponibles' :
                        configuredProps.length === 0 ? '🔧 Configure al menos una propiedad disponible' :
                        '✅ Listo para crear la entidad';
               })()}
            </div>
          </div>

          {/* Columna 2: Propiedades Seleccionadas */}
          <div style={{
            background: '#242424',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid #444'
          }}>
            <h3 style={{
              color: '#8b5cf6',
              margin: '0 0 20px 0',
              fontSize: '18px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              📋 Propiedades Seleccionadas ({selectedProperties.length})
            </h3>

            <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
              {selectedProperties.map(propName => {
                const propType = classProperties[propName];
                const isConfigurable = isPropertyConfigurable(propName, propType);
                
                return (
                  <div key={propName} style={{
                    background: isConfigurable ? '#1a1a1a' : '#2a1a1a',
                    borderRadius: '8px',
                    padding: '12px',
                    marginBottom: '12px',
                    border: `1px solid ${isConfigurable ? '#444' : '#f59e0b'}`,
                    opacity: isConfigurable ? 1 : 0.8
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '8px'
                    }}>
                      <div style={{ 
                        color: '#fff', 
                        fontWeight: '600', 
                        fontSize: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}>
                        {propName}
                        {!isConfigurable && <span style={{ fontSize: '12px', color: '#f59e0b' }}>⚠️</span>}
                      </div>
                      <button
                        onClick={() => handlePropertySelection(propName)}
                        style={{
                          background: '#ef4444',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '4px',
                          padding: '2px 6px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        ✕
                      </button>
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '12px', marginBottom: '8px' }}>
                      Tipo: {propType} 
                      {!isConfigurable && (
                        <span style={{ color: '#f59e0b' }}>
                          {isPrimitiveType(propType) ? ' (No configurable)' : ' (Sin instancias)'}
                        </span>
                      )}
                    </div>
                    {isConfigurable ? (
                      renderPropertyInput(propName, propType)
                    ) : (
                      <div style={{
                        padding: '12px 16px',
                        background: '#2a1a1a',
                        borderRadius: '6px',
                        color: '#f59e0b',
                        fontSize: '12px',
                        textAlign: 'center',
                        boxSizing: 'border-box'
                      }}>
                        {isPrimitiveType(propType) 
                          ? '⚠️ Tipo no implementado para configuración'
                          : '⚠️ No hay instancias disponibles para seleccionar'
                        }
                      </div>
                    )}
                  </div>
                );
              })}
              
              {selectedProperties.length === 0 && (
                <div style={{
                  textAlign: 'center',
                  color: '#6b7280',
                  fontSize: '14px',
                  padding: '40px 20px'
                }}>
                  Selecciona propiedades de la lista para configurar sus valores
                </div>
              )}
            </div>
          </div>

          {/* Columna 3: Preview del Nodo */}
          <div style={{
            background: '#242424',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid #444'
          }}>
            <h3 style={{
              color: '#f97316',
              margin: '0 0 20px 0',
              fontSize: '18px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              👁️ Preview del Nodo
            </h3>

            {entityName && entityClass ? (
              <div style={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                borderRadius: '12px',
                padding: '20px',
                color: '#fff',
                textAlign: 'center'
              }}>
                <div style={{
                  fontSize: '32px',
                  marginBottom: '12px'
                }}>
                  🏗️
                </div>
                <div style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  marginBottom: '8px'
                }}>
                  {entityName}
                </div>
                <div style={{
                  fontSize: '14px',
                  opacity: 0.9,
                  marginBottom: '16px'
                }}>
                  {entityClass}
                </div>
                
                <div style={{ textAlign: 'left' }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    marginBottom: '8px'
                  }}>
                    Configuración:
                  </div>
                  <div style={{ fontSize: '12px', marginBottom: '4px' }}>
                    🏷️ Nombre: {entityName}
                  </div>
                  <div style={{ fontSize: '12px', marginBottom: '4px' }}>
                    🔧 Clase Base: {baseClass}
                  </div>
                  <div style={{ fontSize: '12px', marginBottom: '8px' }}>
                    🏗️ Tipo: {entityClass}
                  </div>
                  
                  {selectedProperties.length > 0 && (
                    <>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        marginBottom: '8px'
                      }}>
                        Propiedades configuradas:
                      </div>
                      {selectedProperties.map(prop => (
                        <div key={prop} style={{ fontSize: '12px', marginBottom: '2px' }}>
                          • {prop}: {(() => {
                            const isConfigurable = isPropertyConfigurable(prop, classProperties[prop]);
                            const value = propertyValues[prop];
                            if (!isConfigurable) return '(No configurable)';
                            return value || 'Pendiente de configurar';
                          })()}
                        </div>
                      ))}
                    </>
                  )}
                </div>
              </div>
            ) : (
              <div style={{
                textAlign: 'center',
                color: '#6b7280',
                fontSize: '14px',
                padding: '60px 20px'
              }}>
                Completa el nombre y selecciona una clase para ver el preview
              </div>
            )}

            {/* Sección de eliminación */}
            <div style={{
              marginTop: '40px',
              padding: '16px',
              background: '#2d1b1b',
              borderRadius: '8px',
              border: '1px solid #ef4444'
            }}>
              <h4 style={{
                color: '#ef4444',
                margin: '0 0 12px 0',
                fontSize: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                🗑️ Eliminar Entidad Existente
              </h4>
              
              <input
                type="text"
                placeholder="Escriba el nombre exacto de la entidad..."
                value={deletingEntity}
                onChange={(e) => setDeletingEntity(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '6px',
                  border: '1px solid #ef4444',
                  background: '#1a1a1a',
                  color: '#fff',
                  fontSize: '14px',
                  marginBottom: '8px',
                  boxSizing: 'border-box'
                }}
              />
              
              <button
                onClick={() => deleteEntity(deletingEntity)}
                disabled={!deletingEntity.trim()}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: deletingEntity.trim() ? '#ef4444' : '#6b7280',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: deletingEntity.trim() ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s ease',
                  boxSizing: 'border-box'
                }}
              >
                🗑️ Eliminar "{deletingEntity || 'entidad'}"
              </button>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AdminPanelModal;