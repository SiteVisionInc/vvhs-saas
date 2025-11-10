// frontend/src/components/Layout/Navbar.tsx - UPDATED with BH Module
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [bhDropdownOpen, setBhDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const isBHActive = () => {
    return location.pathname.startsWith('/bh');
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/dashboard" className="text-xl font-bold hover:text-blue-100 transition-colors">
            VVHS SaaS
          </Link>
          
          <div className="flex items-center space-x-6">
            <Link 
              to="/dashboard" 
              className={`hover:text-blue-200 transition-colors ${
                isActive('/dashboard') || isActive('/') ? 'font-semibold border-b-2 border-white' : ''
              }`}
            >
              Dashboard
            </Link>
            
            <Link 
              to="/volunteers" 
              className={`hover:text-blue-200 transition-colors ${
                isActive('/volunteers') ? 'font-semibold border-b-2 border-white' : ''
              }`}
            >
              Volunteers
            </Link>
            
            <Link 
              to="/events" 
              className={`hover:text-blue-200 transition-colors ${
                isActive('/events') ? 'font-semibold border-b-2 border-white' : ''
              }`}
            >
              Events
            </Link>
            
            <Link 
              to="/shifts/available" 
              className={`hover:text-blue-200 transition-colors ${
                isActive('/shifts/available') ? 'font-semibold border-b-2 border-white' : ''
              }`}
            >
              Available Shifts
            </Link>
            
            <Link 
              to="/time-entries" 
              className={`hover:text-blue-200 transition-colors ${
                isActive('/time-entries') ? 'font-semibold border-b-2 border-white' : ''
              }`}
            >
              Time Entries
            </Link>
            
            <Link 
              to="/reports" 
              className={`hover:text-blue-200 transition-colors ${
                isActive('/reports') ? 'font-semibold border-b-2 border-white' : ''
              }`}
            >
              📊 Reports
            </Link>
            
            {/* NEW: Behavioral Health Dropdown */}
            <div className="relative">
              <button
                onClick={() => setBhDropdownOpen(!bhDropdownOpen)}
                className={`hover:text-blue-200 transition-colors flex items-center space-x-1 ${
                  isBHActive() ? 'font-semibold border-b-2 border-white' : ''
                }`}
              >
                <span> BH Module</span>
                <svg 
                  className={`w-4 h-4 transition-transform ${bhDropdownOpen ? 'rotate-180' : ''}`}
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {/* Dropdown Menu */}
              {bhDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl py-2 z-50">
                  <Link
                    to="/bh"
                    onClick={() => setBhDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">🏠</span>
                      <div>
                        <div className="font-semibold">BH Dashboard</div>
                        <div className="text-xs text-gray-500">Overview & stats</div>
                      </div>
                    </div>
                  </Link>
                  
                  <hr className="my-2" />
                  
                  <div className="px-4 py-1 text-xs font-semibold text-gray-400 uppercase">
                    Clinical Workflow
                  </div>
                  
                  <Link
                    to="/bh/patients"
                    onClick={() => setBhDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">👤</span>
                      <span>Patients</span>
                    </div>
                  </Link>
                  
                  <Link
                    to="/bh/referrals"
                    onClick={() => setBhDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">📋</span>
                      <span>Referrals</span>
                    </div>
                  </Link>
                  
                  <Link
                    to="/bh/bed-search"
                    onClick={() => setBhDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">🔍</span>
                      <span>Bed Search</span>
                    </div>
                  </Link>
                  
                  <hr className="my-2" />
                  
                  <div className="px-4 py-1 text-xs font-semibold text-gray-400 uppercase">
                    Facility Management
                  </div>
                  
                  <Link
                    to="/bh/facilities"
                    onClick={() => setBhDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">🏢</span>
                      <span>Facilities</span>
                    </div>
                  </Link>
                  
                  <Link
                    to="/bh/beds"
                    onClick={() => setBhDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">🛏️</span>
                      <span>Bed Availability</span>
                    </div>
                  </Link>
                  
                  <Link
                    to="/bh/stale-beds"
                    onClick={() => setBhDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">⚠️</span>
                      <span>Stale Data Alerts</span>
                    </div>
                  </Link>
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4 border-l border-blue-500 pl-6">
              <span className="text-sm">
                {user?.first_name} {user?.last_name}
                <span className="ml-2 text-xs bg-blue-700 px-2 py-1 rounded">
                  {user?.role}
                </span>
              </span>
              <button
                onClick={handleLogout}
                className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};