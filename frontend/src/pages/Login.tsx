import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setDebugInfo([]);
    setLoading(true);

    const debug: string[] = [];
    
    try {
      debug.push(`[${new Date().toISOString()}] Starting login attempt`);
      debug.push(`Username: ${username}`);
      debug.push(`Password length: ${password.length} characters`);
      debug.push(`API URL: ${window.location.origin}/api`);
      
      console.log('Login attempt:', { username, passwordLength: password.length });
      
      await login(username, password);
      
      debug.push('✅ Login successful! Redirecting to dashboard...');
      console.log('Login successful, navigating to dashboard...');
      
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 100);
      
    } catch (err: any) {
      console.error('Full error object:', err);
      debug.push('❌ Login failed with error:');
      
      // Extremely detailed error breakdown
      let detailedError = 'Network Error - Unable to reach authentication server\n\n';
      
      if (err.code === 'ERR_NETWORK') {
        detailedError += '🔴 ERROR TYPE: Network Connection Failed\n\n';
        detailedError += 'POSSIBLE CAUSES:\n';
        detailedError += '1. The API server is not responding\n';
        detailedError += '2. CORS (Cross-Origin Resource Sharing) is blocking the request\n';
        detailedError += '3. The frontend is using the wrong API URL\n';
        detailedError += '4. Network proxy or firewall is blocking the connection\n\n';
        
        detailedError += 'TECHNICAL DETAILS:\n';
        detailedError += `• Request URL: ${window.location.origin}/api/v1/auth/login\n`;
        detailedError += `• Request Method: POST\n`;
        detailedError += `• Browser: ${navigator.userAgent.substring(0, 50)}...\n`;
        
        if (err.config) {
          detailedError += `• Base URL: ${err.config.baseURL || 'Not set'}\n`;
          detailedError += `• Full URL: ${err.config.url || 'Not set'}\n`;
          detailedError += `• Headers: ${JSON.stringify(err.config.headers || {})}\n`;
        }
        
        detailedError += '\nDEBUGGING STEPS:\n';
        detailedError += '1. Open browser console (F12) and check Network tab\n';
        detailedError += '2. Look for the failed request to /api/v1/auth/login\n';
        detailedError += '3. Check if request shows CORS error or connection refused\n';
        detailedError += '4. Try this in console:\n';
        detailedError += "   fetch('/api/v1/auth/login', {\n";
        detailedError += "     method: 'POST',\n";
        detailedError += "     headers: {'Content-Type': 'application/json'},\n";
        detailedError += "     body: JSON.stringify({\n";
        detailedError += "       username: 'admin@vdh.virginia.gov',\n";
        detailedError += "       password: 't3st45#!$6!'\n";
        detailedError += "     })\n";
        detailedError += "   }).then(r => r.json()).then(console.log)\n";
        
        debug.push('Network error - Cannot connect to API');
        debug.push(`Error code: ${err.code}`);
        debug.push(`Error message: ${err.message}`);
        
      } else if (err.response) {
        // Server responded with error
        const status = err.response.status;
        const data = err.response.data;
        
        detailedError = `🔴 SERVER ERROR: HTTP ${status}\n\n`;
        
        if (status === 401) {
          detailedError += 'AUTHENTICATION FAILED\n\n';
          detailedError += 'The username or password is incorrect.\n\n';
          detailedError += 'DETAILS:\n';
          detailedError += `• Username tried: ${username}\n`;
          detailedError += `• Password length: ${password.length} characters\n`;
          detailedError += `• Server message: ${data?.detail || 'Invalid credentials'}\n\n`;
          detailedError += 'SOLUTIONS:\n';
          detailedError += '1. Verify the password is correct\n';
          detailedError += '2. The correct password might be: t3st45#!$6!\n';
          detailedError += '3. Check if caps lock is on\n';
          detailedError += '4. Try copying and pasting the password\n';
          
        } else if (status === 404) {
          detailedError += 'ENDPOINT NOT FOUND\n\n';
          detailedError += 'The login API endpoint does not exist.\n\n';
          detailedError += 'DETAILS:\n';
          detailedError += `• Requested: ${err.config?.url}\n`;
          detailedError += `• Base URL: ${err.config?.baseURL}\n\n`;
          detailedError += 'This means the backend API is not properly configured.';
          
        } else if (status === 500) {
          detailedError += 'INTERNAL SERVER ERROR\n\n';
          detailedError += 'The backend server encountered an error.\n\n';
          detailedError += 'DETAILS:\n';
          detailedError += `• Server message: ${JSON.stringify(data)}\n`;
          detailedError += 'Check the backend logs: docker logs vvhs-api --tail 50\n';
          
        } else {
          detailedError += `HTTP ERROR ${status}\n\n`;
          detailedError += `Server response: ${JSON.stringify(data)}\n`;
        }
        
        debug.push(`Server error: HTTP ${status}`);
        debug.push(`Response: ${JSON.stringify(data)}`);
        
      } else if (err.request) {
        // Request made but no response
        detailedError = '🔴 NO RESPONSE FROM SERVER\n\n';
        detailedError += 'The request was sent but no response was received.\n\n';
        detailedError += 'POSSIBLE CAUSES:\n';
        detailedError += '1. Backend server is down\n';
        detailedError += '2. Request timeout\n';
        detailedError += '3. Network interruption\n\n';
        detailedError += 'Check if API is running: docker ps | grep vvhs-api\n';
        
        debug.push('No response from server');
        debug.push('Request was sent but timed out');
        
      } else {
        // Other error
        detailedError = '🔴 UNEXPECTED ERROR\n\n';
        detailedError += `Error message: ${err.message}\n\n`;
        detailedError += 'Full error details:\n';
        detailedError += JSON.stringify(err, null, 2);
        
        debug.push(`Unexpected error: ${err.message}`);
      }
      
      setError(detailedError);
      setDebugInfo(debug);
      
    } finally {
      setLoading(false);
    }
  };

  const fillTestCredentials = () => {
    setUsername('admin@vdh.virginia.gov');
    setPassword('t3st45#!$6!');
    setError('');
    setDebugInfo(['Test credentials filled', 'Password: t3st45#!$6!']);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-4">
      <div className="max-w-2xl w-full space-y-6">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            VVHS Volunteer Management
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4 border-2 border-red-200">
              <pre className="text-xs text-red-800 whitespace-pre-wrap font-mono">
                {error}
              </pre>
            </div>
          )}
          
          {showDebug && debugInfo.length > 0 && (
            <div className="rounded-md bg-blue-50 p-4 border-2 border-blue-200">
              <h4 className="text-sm font-bold text-blue-900 mb-2">Debug Information:</h4>
              {debugInfo.map((info, i) => (
                <div key={i} className="text-xs text-blue-700 font-mono">
                  {info}
                </div>
              ))}
            </div>
          )}
          
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Username or Email"
              />
            </div>
            <div>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
          
          <div className="flex justify-between items-center">
            <button
              type="button"
              onClick={fillTestCredentials}
              className="text-sm text-indigo-600 hover:text-indigo-500"
            >
              Use test credentials
            </button>
            
            <button
              type="button"
              onClick={() => setShowDebug(!showDebug)}
              className="text-sm text-gray-600 hover:text-gray-500"
            >
              {showDebug ? 'Hide' : 'Show'} debug info
            </button>
          </div>
        </form>
        
        <div className="mt-6 p-4 bg-gray-100 rounded-md">
          <h4 className="text-sm font-bold text-gray-700 mb-2">Quick Debug Test:</h4>
          <button
            onClick={() => {
              fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                  username: 'admin@vdh.virginia.gov',
                  password: 't3st45#!$6!'
                })
              })
              .then(r => r.json())
              .then(data => {
                setDebugInfo([
                  '✅ Direct fetch successful!',
                  `Token received: ${data.access_token?.substring(0, 50)}...`,
                  'The API is working correctly.',
                  'The issue might be with the frontend axios configuration.'
                ]);
              })
              .catch(err => {
                setDebugInfo([
                  '❌ Direct fetch failed',
                  `Error: ${err.message}`,
                  'The API connection has issues.'
                ]);
              });
            }}
            className="text-sm bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700"
          >
            Test API Connection Directly
          </button>
        </div>
      </div>
    </div>
  );
};