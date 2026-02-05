/**
 * Authentication service for API calls.
 */
import api from './api';
import type {
  RegisterRequest,
  TokenResponse,
  User,
  MessageResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
} from '../types';

export const authService = {
  /**
   * Register a new user.
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Login with email and password.
   * 
   * Security: Uses OAuth2 password flow (form data, not JSON).
   */
  async login(email: string, password: string): Promise<TokenResponse> {
    // OAuth2 requires form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 uses 'username' field
    formData.append('password', password);

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store tokens securely
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    if (response.data.refresh_token) {
      localStorage.setItem('refresh_token', response.data.refresh_token);
    }

    return response.data;
  },

  /**
   * Logout current user.
   * 
   * Security: Removes tokens from localStorage.
   */
  async logout(): Promise<MessageResponse> {
    try {
      const response = await api.post<MessageResponse>('/auth/logout');
      return response.data;
    } finally {
      // Always remove tokens, even if API call fails
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  /**
   * Get current user profile.
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  /**
   * Check if user is authenticated.
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  
  /**
   * Request password reset email.
   */
  async forgotPassword(data: ForgotPasswordRequest): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>('/auth/forgot-password', data);
    return response.data;
  },

  /**
   * Reset password with token.
   */
  async resetPassword(data: ResetPasswordRequest): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>('/auth/reset-password', data);
    return response.data;
  },

  /**
   * Change password (for logged in user).
   */
  async changePassword(data: ChangePasswordRequest): Promise<MessageResponse> {
    const response = await api.put<MessageResponse>('/users/me/password', {
      old_password: data.current_password,
      new_password: data.new_password,
    });
    return response.data;
  },
};
