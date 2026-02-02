/**
 * ContactList component - displays all contacts with search.
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { contactService } from '../../services/contactService';
import type { Contact } from '../../types';

export const ContactList: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadContacts = async (searchQuery?: string) => {
    setLoading(true);
    setError('');
    
    try {
      const data = await contactService.getContacts(searchQuery);
      setContacts(data);
    } catch (err: any) {
      setError('Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContacts();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadContacts(search);
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Delete contact "${name}"?`)) return;
    
    try {
      await contactService.deleteContact(id);
      setContacts(contacts.filter(c => c.id !== id));
    } catch (err) {
      alert('Failed to delete contact');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl">Loading contacts...</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Contacts</h1>
        <Link to="/contacts/new" className="btn-primary">
          + Add Contact
        </Link>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search by name, email, phone or company..."
            className="input-field flex-1"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn-primary">
            Search
          </button>
          {search && (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setSearch('');
                loadContacts();
              }}
            >
              Clear
            </button>
          )}
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Contacts List */}
      {contacts.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-xl mb-4">No contacts found</p>
          <Link to="/contacts/new" className="text-blue-600 hover:text-blue-700">
            Create your first contact
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contacts.map((contact) => (
            <div key={contact.id} className="card hover:shadow-lg transition-shadow flex flex-col">
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-2">{contact.name}</h3>
                
                {contact.company && (
                  <p className="text-gray-600 mb-1">
                    <span className="font-medium">Company:</span> {contact.company}
                  </p>
                )}
                
                {contact.position && (
                  <p className="text-gray-600 mb-1">
                    <span className="font-medium">Position:</span> {contact.position}
                  </p>
                )}
                
                {contact.email && (
                  <p className="text-gray-600 mb-1">
                    <span className="font-medium">Email:</span> {contact.email}
                  </p>
                )}
              </div>
              
              <div className="mt-4 flex gap-2">
                <Link
                  to={`/contacts/${contact.id}`}
                  className="btn-primary flex-1 text-center"
                >
                  View
                </Link>
                <button
                  onClick={() => handleDelete(contact.id, contact.name)}
                  className="btn-danger"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
