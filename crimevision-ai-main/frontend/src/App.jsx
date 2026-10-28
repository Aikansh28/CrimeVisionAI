import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import CasePage from './pages/CasePage';

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-900 text-white">
        {/* Sidebar is always visible */}
        <Sidebar />

        {/* Main content area */}
        <div className="flex-1 ml-60 min-h-screen">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/case/:id" element={<CasePage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
