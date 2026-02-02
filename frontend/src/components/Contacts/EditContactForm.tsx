/**
 * EditContactForm component - edit existing contact.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { contactService } from '../../services/contactService';
import { validation } from '../../utils/validation';
import type { ContactWithPhones } from '../../types';

export const EditContactForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    position: '',
    address: '',
    notes: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [loadingContact, setLoadingContact] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadContact = async () => {
      if (!id) return;
      
      try {
        const contact = await contactService.getContact(parseInt(id));
        setFormData({
          name: contact.name || '',
          email: contact.email || '',
          company: contact.company || '',
          position: contact.position || '',
          address: contact.address || '',
          notes: contact.notes || '',
        });
      } catch (err) {
        setError('Failed to load contact');
      } finally {
        setLoadingContact(false);
      }
    };
    
    loadContact();
  }, [id]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    // Validate name
    const nameError = validation.required(formData.name, 'Name');
    if (nameError) newErrors.name = nameError;
    
    // Validate email if provided
    if (formData.email) {
      const emailError = validation.email(formData.email);
      if (emailError) newErrors.email = emailError;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!id || !validateForm()) return;
    
    setLoading(true);
    setError('');
    
    try {
      await contactService.updateContact(parseInt(id), {
        name: formData.name,
        email: formData.email || undefined,
        company: formData.company || undefined,
        position: formData.position || undefined,
        address: formData.address || undefined,
        notes: formData.notes || undefined,
      });
      
      navigate(`/contacts/${id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update contact');
    } finally {
      setLoading(false);
    }
  };

  if (loadingContact) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Edit Contact</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name *
            </label>
            <input
              type="text"
              className={`input-field ${errors.name ? 'border-red-500' : ''}`}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            {errors.name && (
              <p className="text-red-500 text-sm mt-1">{errors.name}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              className={`input-field ${errors.email ? 'border-red-500' : ''}`}
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
            {errors.email && (
              <p className="text-red-500 text-sm mt-1">{errors.email}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company
            </label>
            <input
              type="text"
              className="input-field"
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Position
            </label>
            <input
              type="text"
              className="input-field"
              value={formData.position}
              onChange={(e) => setFormData({ ...formData, position: e.target.value })}
            />
          </div>
        </div>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Address
          </label>
          <input
            type="text"
            className="input-field"
            value={formData.address}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            className="input-field"
            rows={3}
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          />
        </div>
        
        <p className="text-sm text-gray-500 mb-6">
          💡 Tip: Manage phone numbers from the contact details page.
        </p>
        
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            type="button"
            onClick={() => navigate(`/contacts/${id}`)}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
