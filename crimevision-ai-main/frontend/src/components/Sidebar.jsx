import React from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, Home } from 'lucide-react';

function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-[#0a0a1a] border-r border-gray-800 flex flex-col z-50">
      {/* Logo / Title */}
      <div className="p-5 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="text-lg font-bold text-white">CrimeVision</h1>
            <p className="text-xs text-blue-400">AI Forensics</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`
          }
        >
          <Home className="w-5 h-5" />
          <span className="text-sm font-medium">Dashboard</span>
        </NavLink>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <p className="text-xs text-gray-500 text-center">CrimeVision AI v1.0</p>
      </div>
    </aside>
  );
}

export default Sidebar;
