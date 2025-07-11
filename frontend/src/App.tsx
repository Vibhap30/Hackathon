import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'

// Components
import Navbar from './components/Navbar'
import Footer from './components/Footer'

// Pages
import HomePage from './pages/HomePage'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import EnergyMarketplace from './pages/EnergyMarketplace'
import EnergyMap from './pages/EnergyMap'
import Community from './pages/Community'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import AIAssistant from './pages/AIAssistant'
import AgentDashboard from './pages/AgentDashboard'

// Services
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-green-50 flex flex-col">
          <Navbar />
          
          <main className="flex-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/marketplace" element={<EnergyMarketplace />} />
                <Route path="/energy-map" element={<EnergyMap />} />
                <Route path="/community" element={<Community />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/ai-assistant" element={<AIAssistant />} />
                <Route path="/agent-dashboard" element={<AgentDashboard />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </motion.div>
          </main>
          
          <Footer />
        </div>
    </AuthProvider>
  )
}

export default App
