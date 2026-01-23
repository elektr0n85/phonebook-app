/**
 * ContactForm component - create new contact with phones.
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { contactService } from '../../services/contactService';
import { validation } from '../../utils/validation';
import type { ContactCreateInput, PhoneInput } from '../../types';

interface PhoneFormData {
  phone_number: string;
  phone_type: 'mobile' | 'landline' | 'internal';
  is_primary: boolean;
  label: string;
}

export const ContactForm: React.FC = () => {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    position: '',
    address: '',
    notes: '',
  });
  
  const [phones, setPhones] = useState<PhoneFormData[]>([
    { phone_number: '', phone_type: 'mobile', is_primary: true, label: '' },
  ]);
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

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
    
    // Validate phones
    phones.forEach((phone, index) => {
      if (phone.phone_number) {
        const phoneError = validation.phone(phone.phone_number, phone.phone_type);
        if (phoneError) {
          newErrors[`phone_${index}`] = phoneError;
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      // Prepare contact data
      const contactData: ContactCreateInput = {
        name: formData.name,
        email: formData.email || undefined,
        company: formData.company || undefined,
        position: formData.position || undefined,
        address: formData.address || undefined,
        notes: formData.notes || undefined,
        phones: phones
          .filter(p => p.phone_number.trim())
          .map(p => ({
            phone_data: {
              phone_number: p.phone_number,
              phone_type: p.phone_type,
            },
            is_primary: p.is_primary,
            label: p.label || undefined,
          })),
      };
      
      const contact = await contactService.createContact(contactData);
      console.log('Contact created:', contact);
      navigate(`/contacts/${contact.id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create contact');
    } finally {
      setLoading(false);
    }
  };

  const addPhone = () => {
    setPhones([
      ...phones,
      { phone_number: '', phone_type: 'mobile', is_primary: false, label: '' },
    ]);
  };

  const removePhone = (index: number) => {
    setPhones(phones.filter((_, i) => i !== index));
  };

  const updatePhone = (index: number, field: keyof PhoneFormData, value: any) => {
    const newPhones = [...phones];
    newPhones[index] = { ...newPhones[index], [field]: value };
    
    // If setting as primary, unset others
    if (field === 'is_primary' && value === true) {
      newPhones.forEach((p, i) => {
        if (i !== index) p.is_primary = false;
      });
    }
    
    setPhones(newPhones);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Create New Contact</h1>
      
      <form onSubmit={handleSubmit} className="card">
        {/* Basic Information */}
        <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
        
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

        {/* Phone Numbers */}
        <h2 className="text-xl font-semibold mb-4">Phone Numbers</h2>
        
        {phones.map((phone, index) => (
          <div key={index} className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  type="text"
                  className={`input-field ${
                    errors[`phone_${index}`] ? 'border-red-500' : ''
                  }`}
                  placeholder="+48123456789"
                  value={phone.phone_number}
                  onChange={(e) =>
                    updatePhone(index, 'phone_number', e.target.value)
                  }
                />
                {errors[`phone_${index}`] && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors[`phone_${index}`]}
                  </p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type
                </label>
                <select
                  className="input-field"
                  value={phone.phone_type}
                  onChange={(e) =>
                    updatePhone(index, 'phone_type', e.target.value)
                  }
                >
                  <option value="mobile">Mobile</option>
                  <option value="landline">Landline</option>
                  <option value="internal">Internal</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Label
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Personal, Work, etc."
                  value={phone.label}
                  onChange={(e) => updatePhone(index, 'label', e.target.value)}
                />
              </div>
            </div>
            
            <div className="mt-2 flex items-center gap-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="mr-2"
                  checked={phone.is_primary}
                  onChange={(e) =>
                    updatePhone(index, 'is_primary', e.target.checked)
                  }
                />
                <span className="text-sm">Primary phone</span>
              </label>
              
              {phones.length > 1 && (
                <button
                  type="button"
                  onClick={() => removePhone(index)}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Remove
                </button>
              )}
            </div>
          </div>
        ))}
        
        <button
          type="button"
          onClick={addPhone}
          className="btn-secondary mb-6"
        >
          + Add Another Phone
        </button>

        {/* Submit */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Creating...' : 'Create Contact'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/contacts')}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
