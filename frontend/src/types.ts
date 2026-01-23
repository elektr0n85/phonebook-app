/**
 * TypeScript types for API models.
 * These should match backend Pydantic schemas.
 */

export interface User {
  id: number;
  email: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface Contact {
  id: number;
  name: string;
  email?: string;
  address?: string;
  notes?: string;
  company?: string;
  position?: string;
  created_at: string;
  updated_at: string;
}

export interface Phone {
  id: number;
  phone_number: string;
  phone_type: 'mobile' | 'landline' | 'internal';
  country_code?: string;
  area_code?: string;
  local_number?: string;
  extension?: string;
  created_at: string;
}

export interface ContactPhone {
  id: number;
  phone: Phone;
  is_primary: boolean;
  label?: string;
  notes?: string;
  created_at: string;
}

export interface ContactWithPhones extends Contact {
  phones: ContactPhone[];
}

export interface LoginRequest {
  username: string; // OAuth2 uses 'username' field
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}

export interface ErrorResponse {
  detail: string;
}

export interface PhoneInput {
  phone_number: string;
  phone_type: 'mobile' | 'landline' | 'internal';
}

export interface ContactPhoneInput {
  phone_data?: PhoneInput;
  phone_id?: number;
  is_primary?: boolean;
  label?: string;
  notes?: string;
}

export interface ContactCreateInput {
  name: string;
  email?: string;
  address?: string;
  notes?: string;
  company?: string;
  position?: string;
  phones?: ContactPhoneInput[];
}

export interface ContactUpdateInput {
  name?: string;
  email?: string;
  address?: string;
  notes?: string;
  company?: string;
  position?: string;
}
