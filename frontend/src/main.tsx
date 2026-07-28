import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import { Toast, Typography } from '@heroui/react'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Toast.Provider/>
    <Typography.Prose>
    <App />
    </Typography.Prose>
  </StrictMode>,
)
