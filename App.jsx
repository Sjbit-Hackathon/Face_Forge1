import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Session from './pages/Session';
import Export from './pages/Export';
import Audit from './pages/Audit';
import Navbar from './components/Navbar';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={
          <div className="app-layout">
            <Navbar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/session/:id" element={<Session />} />
                <Route path="/session/:id/export" element={<Export />} />
                <Route path="/audit" element={<Audit />} />
              </Routes>
            </main>
          </div>
        } />
      </Routes>
    </div>
  );
}

export default App;
