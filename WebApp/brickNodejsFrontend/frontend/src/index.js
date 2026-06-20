// src/index.js

// 1) Importa el CSS base de React Flow (el que sí existe en tu node_modules)
import 'reactflow/dist/style.css'

// 2) Ahora tu CSS global y el turbo.css que hayas creado
import './index.css'
import './turbo.css'

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import reportWebVitals from './reportWebVitals'

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

reportWebVitals()

