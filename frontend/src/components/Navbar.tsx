
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BoltIcon,
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  ChartBarIcon,
  ShoppingCartIcon,
  BuildingOfficeIcon,
  CpuChipIcon,
  GlobeAltIcon,
  Cog6ToothIcon,
  WalletIcon
} from '@heroicons/react/24/outline'

const Navbar: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false)

  const navItems = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon },
    { name: 'Marketplace', href: '/marketplace', icon: ShoppingCartIcon },
    { name: 'Community', href: '/community', icon: BuildingOfficeIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'AI Assistant', href: '/ai-assistant', icon: CpuChipIcon },
    { name: 'Agents', href: '/agent-dashboard', icon: CpuChipIcon },
    { name: 'Beckn Protocol', href: '/beckn-protocol', icon: GlobeAltIcon },
   
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
    {name:'Coins',href:'/coins',icon:WalletIcon}
    
  ]

  return (
    <nav className="bg-white/90 backdrop-blur-md shadow-lg sticky top-0 z-50 border-b border-green-100">
      <div className="container-main">
        <div className="flex justify-between items-center h-16 ml-[-3%]">

          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <BoltIcon className="h-6 w-6 text-green-500" />
            <span className="text-xl font-bold text-gradient">PowerShare</span>
          </Link>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden">
            <button onClick={() => setMenuOpen(!menuOpen)}>
              {menuOpen ? (
                <XMarkIcon className="h-6 w-6 text-green-600" />
              ) : (
                <Bars3Icon className="h-6 w-6 text-green-600" />
              )}
            </button>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center space-x-2 text-gray-700 hover:text-green-600 hover:bg-green-50 px-3 py-1 rounded-xl text-sm font-medium transition-all duration-200 group"
              >
                <item.icon className="h-5 w-5 text-green-500" />
                <span className="whitespace-nowrap">{item.name}</span>
              </Link>
            ))}
            {/* <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-3 py-1.5 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg shadow-sm transition duration-200"
            >
              Connect
            </motion.button> */}
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden flex flex-col space-y-2 mt-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center space-x-2 text-gray-700 hover:text-green-600 hover:bg-green-50 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200"
              >
                <item.icon className="h-5 w-5 text-green-500" />
                <span className="whitespace-nowrap">{item.name}</span>
              </Link>
            ))}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md shadow-sm transition duration-200"
            >
              Connect
            </motion.button>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
