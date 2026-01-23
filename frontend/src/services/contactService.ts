/**
 * Contacts service for API calls.
 */
import api from './api';
import type {
  Contact,
  ContactWithPhones,
  ContactCreateInput,
  ContactUpdateInput,
  ContactPhoneInput,
  MessageResponse,
  ContactPhone,
} from '../types';

export const contactService = {
  /**
   * Get all contacts for current user.
   */
  async getContacts(search?: string): Promise<Contact[]> {
    const params = search ? { search } : {};
    const response = await api.get<Contact[]>('/contacts', { params });
    return response.data;
  },

  /**
   * Get contact by ID with phones.
   */
  async getContact(id: number): Promise<ContactWithPhones> {
    const response = await api.get<ContactWithPhones>(`/contacts/${id}`);
    return response.data;
  },

  /**
   * Create a new contact with phones.
   */
  async createContact(data: ContactCreateInput): Promise<ContactWithPhones> {
    const response = await api.post<ContactWithPhones>('/contacts', data);
    return response.data;
  },

  /**
   * Update contact information.
   */
  async updateContact(
    id: number,
    data: ContactUpdateInput
  ): Promise<Contact> {
    const response = await api.put<Contact>(`/contacts/${id}`, data);
    return response.data;
  },

  /**
   * Delete contact (soft delete).
   */
  async deleteContact(id: number): Promise<MessageResponse> {
    const response = await api.delete<MessageResponse>(`/contacts/${id}`);
    return response.data;
  },

  /**
   * Add phone to contact.
   */
  async addPhone(
    contactId: number,
    phoneData: ContactPhoneInput
  ): Promise<ContactPhone> {
    const response = await api.post<ContactPhone>(
      `/contacts/${contactId}/phones`,
      phoneData
    );
    return response.data;
  },

  /**
   * Remove phone from contact.
   */
  async removePhone(
    contactId: number,
    phoneId: number
  ): Promise<MessageResponse> {
    const response = await api.delete<MessageResponse>(
      `/contacts/${contactId}/phones/${phoneId}`
    );
    return response.data;
  },

  /**
   * Set phone as primary for contact.
   */
  async setPrimaryPhone(
    contactId: number,
    phoneId: number
  ): Promise<ContactPhone> {
    const response = await api.put<ContactPhone>(
      `/contacts/${contactId}/phones/${phoneId}/primary`
    );
    return response.data;
  },
};
