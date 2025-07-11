import React from 'react'
import { BoltIcon } from '@heroicons/react/24/outline'

const Footer: React.FC = () => {
  return (
    <footer className="bg-gradient-to-r from-slate-900 via-blue-900 to-green-900 text-white">
      <div className="container-main py-12">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <BoltIcon className="logo-icon text-green-400" />
              <span className="text-xl font-bold">PowerShare</span>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed">
              Empowering communities through decentralized energy trading powered by AI and blockchain technology.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-green-400">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="/dashboard" className="text-gray-300 hover:text-green-400 transition-colors">Dashboard</a></li>
              <li><a href="/marketplace" className="text-gray-300 hover:text-green-400 transition-colors">Marketplace</a></li>
              <li><a href="/community" className="text-gray-300 hover:text-green-400 transition-colors">Community</a></li>
              <li><a href="/analytics" className="text-gray-300 hover:text-green-400 transition-colors">Analytics</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-green-400">Technology</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>🔗 Blockchain Security</li>
              <li>🤖 AI Optimization</li>
              <li>🌐 Beckn Protocol</li>
              <li>☁️ Cloud-Native</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-sm text-gray-400">
            © 2025 PowerShare. All rights reserved. Built with ❤️ for sustainable energy future.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
