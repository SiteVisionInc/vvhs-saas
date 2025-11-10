import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
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
			    {/* NEW: Reports Link */}
            <Link 
              to="/reports" 
              className={`hover:text-blue-200 transition-colors ${
                isActive('/reports') ? 'font-semibold border-b-2 border-white' : ''
              }`}
            >
              📊 Reports
            </Link>
            
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