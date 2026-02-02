/**
 * AddPhoneForm component - add phone to existing contact.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { contactService } from '../../services/contactService';
import { validation } from '../../utils/validation';
import type { ContactWithPhones } from '../../types';

export const AddPhoneForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [contact, setContact] = useState<ContactWithPhones | null>(null);
  const [formData, setFormData] = useState({
    phone_number: '',
    phone_type: 'mobile' as 'mobile' | 'landline' | 'internal',
    is_primary: false,
    label: '',
    notes: '',
  });
  
  const [error, setError] = useState('');
  const [fieldError, setFieldError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingContact, setLoadingContact] = useState(true);

  useEffect(() => {
    const loadContact = async () => {
      if (!id) return;
      
      try {
        const data = await contactService.getContact(parseInt(id));
        setContact(data);
      } catch (err) {
        setError('Failed to load contact');
      } finally {
        setLoadingContact(false);
      }
    };
    
    loadContact();
  }, [id]);

  const validateForm = (): boolean => {
    // Validate phone number
    const phoneError = validation.phone(formData.phone_number, formData.phone_type);
    if (phoneError) {
      setFieldError(phoneError);
      return false;
    }
    
    setFieldError('');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!id || !validateForm()) return;
    
    setLoading(true);
    setError('');
    
    try {
      await contactService.addPhone(parseInt(id), {
        phone_data: {
          phone_number: formData.phone_number,
          phone_type: formData.phone_type,
        },
        is_primary: formData.is_primary,
        label: formData.label || undefined,
        notes: formData.notes || undefined,
      });
      
      navigate(`/contacts/${id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add phone');
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

  if (!contact) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Contact not found
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Add Phone Number</h1>
      <p className="text-gray-600 mb-6">Adding phone to: <strong>{contact.name}</strong></p>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="card">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phone Number *
          </label>
          <input
            type="text"
            className={`input-field ${fieldError ? 'border-red-500' : ''}`}
            placeholder={
              formData.phone_type === 'mobile' 
                ? '+48123456789' 
                : formData.phone_type === 'landline'
                  ? '171234567'
                  : '1234'
            }
            value={formData.phone_number}
            onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
          />
          {fieldError && (
            <p className="text-red-500 text-sm mt-1">{fieldError}</p>
          )}
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <select
            className="input-field"
            value={formData.phone_type}
            onChange={(e) => setFormData({ 
              ...formData, 
              phone_type: e.target.value as 'mobile' | 'landline' | 'internal' 
            })}
          >
            <option value="mobile">Mobile (+48...)</option>
            <option value="landline">Landline (area code)</option>
            <option value="internal">Internal (extension)</option>
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Label
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="Personal, Work, Office, etc."
            value={formData.label}
            onChange={(e) => setFormData({ ...formData, label: e.target.value })}
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="Additional notes..."
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          />
        </div>
        
        <div className="mb-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              className="mr-2"
              checked={formData.is_primary}
              onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
            />
            <span className="text-sm">Set as primary phone</span>
          </label>
        </div>
        
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Adding...' : 'Add Phone'}
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
