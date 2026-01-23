/**
 * Home page component.
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-6">
          📞 Phonebook App
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Manage your contacts securely with multiple phone numbers support
        </p>

        {isAuthenticated ? (
          <Link to="/contacts" className="btn-primary text-lg px-8 py-3">
            Go to My Contacts
          </Link>
        ) : (
          <div className="space-x-4">
            <Link to="/register" className="btn-primary text-lg px-8 py-3">
              Get Started
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              Login
            </Link>
          </div>
        )}

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
          <div className="card">
            <h3 className="text-xl font-semibold mb-2">🔒 Secure</h3>
            <p className="text-gray-600">
              Industry-standard encryption and security practices
            </p>
          </div>

          <div className="card">
            <h3 className="text-xl font-semibold mb-2">📱 Multi-Phone</h3>
            <p className="text-gray-600">
              Support for mobile, landline, and internal extensions
            </p>
          </div>

          <div className="card">
            <h3 className="text-xl font-semibold mb-2">🔍 Search</h3>
            <p className="text-gray-600">
              Quickly find contacts by name, email, or company
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
