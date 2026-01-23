/**
 * ContactDetail component - view contact with phones.
 */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { contactService } from '../../services/contactService';
import type { ContactWithPhones, ContactPhone } from '../../types';

export const ContactDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  const [contact, setContact] = useState<ContactWithPhones | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadContact = async () => {
    if (!id) return;
    
    setLoading(true);
    setError('');
    
    try {
      const data = await contactService.getContact(parseInt(id));
      setContact(data);
    } catch (err: any) {
      setError('Failed to load contact');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContact();
  }, [id]);

  const handleRemovePhone = async (phoneId: number) => {
    if (!id || !confirm('Remove this phone number?')) return;
    
    try {
      await contactService.removePhone(parseInt(id), phoneId);
      loadContact(); // Reload to show updated phones
    } catch (err) {
      alert('Failed to remove phone');
    }
  };

  const handleSetPrimary = async (phoneId: number) => {
    if (!id) return;
    
    try {
      await contactService.setPrimaryPhone(parseInt(id), phoneId);
      loadContact(); // Reload to show updated phones
    } catch (err) {
      alert('Failed to set primary phone');
    }
  };

  const formatPhoneDisplay = (cp: ContactPhone): string => {
    const { phone } = cp;
    
    if (phone.phone_type === 'mobile' && phone.country_code && phone.local_number) {
      return `${phone.country_code} ${phone.local_number}`;
    }
    
    if (phone.phone_type === 'landline' && phone.area_code && phone.local_number) {
      return `(${phone.area_code}) ${phone.local_number}`;
    }
    
    if (phone.phone_type === 'internal' && phone.extension) {
      return `ext. ${phone.extension}`;
    }
    
    return phone.phone_number;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl">Loading contact...</div>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error || 'Contact not found'}
        </div>
        <Link to="/contacts" className="text-blue-600 hover:text-blue-700 mt-4 inline-block">
          ← Back to contacts
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <Link to="/contacts" className="text-blue-600 hover:text-blue-700">
          ← Back to contacts
        </Link>
        <Link
          to={`/contacts/${id}/edit`}
          className="btn-primary"
        >
          Edit Contact
        </Link>
      </div>

      <div className="card">
        <h1 className="text-3xl font-bold mb-6">{contact.name}</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {contact.email && (
            <div>
              <span className="font-medium text-gray-700">Email:</span>
              <p className="text-gray-900">{contact.email}</p>
            </div>
          )}
          
          {contact.company && (
            <div>
              <span className="font-medium text-gray-700">Company:</span>
              <p className="text-gray-900">{contact.company}</p>
            </div>
          )}
          
          {contact.position && (
            <div>
              <span className="font-medium text-gray-700">Position:</span>
              <p className="text-gray-900">{contact.position}</p>
            </div>
          )}
          
          {contact.address && (
            <div>
              <span className="font-medium text-gray-700">Address:</span>
              <p className="text-gray-900">{contact.address}</p>
            </div>
          )}
        </div>

        {contact.notes && (
          <div className="mb-6">
            <span className="font-medium text-gray-700">Notes:</span>
            <p className="text-gray-900 whitespace-pre-wrap">{contact.notes}</p>
          </div>
        )}

        {/* Phone Numbers */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Phone Numbers</h2>
            <Link
              to={`/contacts/${id}/add-phone`}
              className="btn-secondary text-sm"
            >
              + Add Phone
            </Link>
          </div>
          
          {contact.phones && contact.phones.length > 0 ? (
            <div className="space-y-3">
              {contact.phones.map((cp) => (
                <div
                  key={cp.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-medium">
                        {formatPhoneDisplay(cp)}
                      </span>
                      {cp.is_primary && (
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          PRIMARY
                        </span>
                      )}
                      <span className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded">
                        {cp.phone.phone_type.toUpperCase()}
                      </span>
                    </div>
                    
                    {cp.label && (
                      <p className="text-sm text-gray-600 mt-1">{cp.label}</p>
                    )}
                    
                    {cp.notes && (
                      <p className="text-sm text-gray-500 mt-1">{cp.notes}</p>
                    )}
                  </div>
                  
                  <div className="flex gap-2">
                    {!cp.is_primary && (
                      <button
                        onClick={() => handleSetPrimary(cp.phone.id)}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        Set Primary
                      </button>
                    )}
                    <button
                      onClick={() => handleRemovePhone(cp.phone.id)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No phone numbers yet</p>
          )}
        </div>
      </div>
    </div>
  );
};
