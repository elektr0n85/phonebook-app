/**
 * Main App component with routing.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navigation } from './components/Layout/Navigation';
import { ProtectedRoute } from './components/Common/ProtectedRoute';
import { HomePage } from './pages/HomePage';
import { Login } from './components/Auth/Login';
import { Register } from './components/Auth/Register';
import { ForgotPassword } from './components/Auth/ForgotPassword';
import { ResetPassword } from './components/Auth/ResetPassword';
import { ChangePassword } from './components/Auth/ChangePassword';
import { ContactList } from './components/Contacts/ContactList';
import { ContactDetail } from './components/Contacts/ContactDetail';
import { ContactForm } from './components/Contacts/ContactForm';
import { EditContactForm } from './components/Contacts/EditContactForm'
import { AddPhoneForm } from './components/Contacts/AddPhoneForm';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />

            {/* Protected routes */}
            <Route
              path="/contacts"
              element={
                <ProtectedRoute>
                  <ContactList />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/contacts/new"
              element={
                <ProtectedRoute>
                  <ContactForm />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/contacts/:id"
              element={
                <ProtectedRoute>
                  <ContactDetail />
                </ProtectedRoute>
              }
            />


            <Route
              path="/contacts/:id/edit"
              element={
                <ProtectedRoute>
                  <EditContactForm />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/contacts/:id/add-phone"
              element={
                <ProtectedRoute>
                  <AddPhoneForm />
                </ProtectedRoute>
              }
            />

            <Route
              path="/change-password"
              element={
                <ProtectedRoute>
                  <ChangePassword />
                </ProtectedRoute>
              }
            />

            {/* Catch all - redirect to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
