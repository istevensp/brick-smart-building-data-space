import axios from 'axios';

const api = axios.create({
  baseURL: '/api'    // <- ahora todas las llamadas van a http://localhost:3000/api/... 
                     // y React las reenviará a http://127.0.0.1:8000/api/…
});

export default api;



