import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold">
            VVHS SaaS
          </Link>
          
          <div className="flex items-center space-x-6">
            <Link to="/volunteers" className="hover:text-blue-200">
              Volunteers
            </Link>
            <Link to="/events" className="hover:text-blue-200">
              Events
            </Link>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm">{user?.full_name}</span>
              <button
                onClick={handleLogout}
                className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded"
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
