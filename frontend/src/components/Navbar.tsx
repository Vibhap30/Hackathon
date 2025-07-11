import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  BoltIcon, 
  ChartBarIcon, 
  CogIcon, 
  HomeIcon,
  BuildingOfficeIcon,
  ShoppingCartIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'

const Navbar: React.FC = () => {
  const navItems = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon },
    { name: 'Marketplace', href: '/marketplace', icon: ShoppingCartIcon },
    { name: 'Community', href: '/community', icon: BuildingOfficeIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'AI Assistant', href: '/ai-assistant', icon: CpuChipIcon },
    { name: 'Agents', href: '/agent-dashboard', icon: CpuChipIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ]

  return (
    <nav className="bg-white/90 backdrop-blur-md shadow-lg sticky top-0 z-50 border-b border-green-100">
      <div className="container-main">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <BoltIcon className="logo-icon transition-all duration-300 group-hover:text-green-500 group-hover:scale-110" />
                <div className="absolute inset-0 logo-icon text-green-400 opacity-0 group-hover:opacity-30 transition-opacity duration-300 animate-pulse-slow"></div>
              </div>
              <span className="text-xl font-bold text-gradient group-hover:scale-105 transition-transform duration-300">
                PowerShare
              </span>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center space-x-2 text-gray-700 hover:text-green-600 hover:bg-green-50 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 group"
              >
                <item.icon className="nav-icon group-hover:scale-110 transition-transform duration-200" />
                <span>{item.name}</span>
              </Link>
            ))}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-primary"
            >
              Connect Wallet
            </motion.button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
