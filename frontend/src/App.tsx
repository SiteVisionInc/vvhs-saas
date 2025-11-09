import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Layout/Navbar';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { VolunteerList } from './pages/Volunteers/VolunteerList';
import { EventList } from './pages/Events/EventList';
import { PublicRegistrationWizard } from './pages/Volunteers/PublicRegistrationWizard';
import { RegistrationSuccess } from './pages/Volunteers/RegistrationSuccess';
import { AvailableShifts } from './pages/Scheduling/AvailableShifts';
import { TrainingDashboard } from './pages/Training/TrainingDashboard';
import { TimeEntryList } from './pages/TimeTracking/TimeEntryList';
import { PolicyDocumentLibrary } from './components/Documents/PolicyDocumentLibrary';
import { DocumentVerificationQueue } from './components/Documents/DocumentVerificationQueue';
import { ReportsHub } from './pages/Reports/ReportsHub';
import { ReportLibrary } from './pages/Reports/ReportLibrary';
import { VolunteerHoursReport } from './pages/Reports/VolunteerHoursReport';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const AppContent: React.FC = () => {
  const { isAuthenticated, loading, user } = useAuth();

  console.log(' AppContent rendering');
  console.log(' Is authenticated:', isAuthenticated);
  console.log(' Auth loading:', loading);
  console.log(' User:', user);
  console.log(' Current path:', window.location.pathname);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-xl">Loading authentication...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {isAuthenticated && <Navbar />}
      <Routes>
        {/* PUBLIC ROUTES */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<PublicRegistrationWizard />} />
        <Route path="/registration-success" element={<RegistrationSuccess />} />
        
        {/* PROTECTED ROUTES */}
        <Route 
          path="/" 
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } 
        />
        <Route path="/volunteers" element={<PrivateRoute><VolunteerList /></PrivateRoute>} />
        <Route path="/events" element={<PrivateRoute><EventList /></PrivateRoute>} />
		<Route path="/shifts/available" element={<PrivateRoute><AvailableShifts /></PrivateRoute>} />
		<Route 
			path="/volunteers/:volunteerId/training" 
			element={
				<PrivateRoute>
				<TrainingDashboard />
				</PrivateRoute>
			} 
		/>
		<Route 
		path="/time-entries" 
		element={
			<PrivateRoute>
			<TimeEntryList />
			</PrivateRoute>
		} 
		/>
		<Route 
		    path="/documents/policies" 
			element={
				<PrivateRoute>
				<PolicyDocumentLibrary />
				</PrivateRoute>
			} 
		/>
		<Route 
			path="/documents/verify" 
			element={
				<PrivateRoute>
				<DocumentVerificationQueue />
				</PrivateRoute>
			}
		/>
		<Route 
		path="/reports" 
		element={
			<PrivateRoute>
			<ReportsHub />
			</PrivateRoute>
		} 
		/>
		<Route 
		path="/reports/saved" 
		element={
			<PrivateRoute>
			<ReportLibrary />
			</PrivateRoute>
		} 
		/>
		<Route 
		path="/reports/volunteer-hours" 
		element={
			<PrivateRoute>
			<VolunteerHoursReport />
			</PrivateRoute>
		} 
		/>
        
        {/* Catch all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
