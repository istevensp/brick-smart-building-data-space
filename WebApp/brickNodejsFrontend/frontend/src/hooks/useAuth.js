// src/hooks/useAuth.js
import { useState, useEffect } from 'react'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Cargar datos de autenticación del localStorage al iniciar
  useEffect(() => {
    const savedUser = localStorage.getItem('iot-user')
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        setUser(userData)
      } catch (error) {
        console.error('Error parsing user data:', error)
        localStorage.removeItem('iot-user')
      }
    }
    setLoading(false)
  }, [])

  // Función de login que valida credenciales
  const login = async (rol, password) => {
    console.log('🔍 useAuth.login llamado con:', { rol, password })
    
    return new Promise((resolve, reject) => {
      // Simular delay de autenticación
      setTimeout(() => {
        // Validar credenciales
        let isValid = false
        
        if (rol === 'profesor' && password === 'l@bT3l3m@tic@') {
          isValid = true
        } else if (rol === 'estudiante' && password === 'estudiante') {
          isValid = true
        }

        if (isValid) {
          const userData = {
            rol,
            authenticated: true,
            loginTime: new Date().toISOString()
          }
          
          console.log('✅ Login exitoso, guardando usuario:', userData)
          setUser(userData)
          localStorage.setItem('iot-user', JSON.stringify(userData))
          resolve(userData)
        } else {
          console.log('❌ Credenciales inválidas')
          reject(new Error('Rol o contraseña incorrectos'))
        }
      }, 1000) // Simular 1 segundo de delay
    })
  }

  const logout = () => {
    console.log('🚪 Cerrando sesión')
    setUser(null)
    localStorage.removeItem('iot-user')
  }

  const isAuthenticated = user && user.authenticated
  const isProfesor = user && user.rol === 'profesor'
  const isEstudiante = user && user.rol === 'estudiante'

  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated,
    isProfesor,
    isEstudiante
  }
}