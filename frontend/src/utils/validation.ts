/**
 * Client-side validation utilities.
 * 
 * Security: These validations match backend Pydantic schemas.
 * Never trust client-side validation alone - backend validates too!
 */

export const validation = {
  /**
   * Validate email format.
   */
  email: (value: string): string | null => {
    if (!value) return 'Email is required';
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return 'Invalid email format';
    }
    
    return null;
  },

  /**
   * Validate password strength.
   * 
   * Requirements (must match backend):
   * - At least 8 characters
   * - At least 1 uppercase letter
   * - At least 1 lowercase letter
   * - At least 1 digit
   * - At least 1 special character
   */
  password: (value: string): string | null => {
    if (!value) return 'Password is required';
    
    if (value.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    
    if (!/[A-Z]/.test(value)) {
      return 'Password must contain at least one uppercase letter';
    }
    
    if (!/[a-z]/.test(value)) {
      return 'Password must contain at least one lowercase letter';
    }
    
    if (!/[0-9]/.test(value)) {
      return 'Password must contain at least one digit';
    }
    
    const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    if (!specialChars.split('').some(char => value.includes(char))) {
      return 'Password must contain at least one special character';
    }
    
    return null;
  },

  /**
   * Validate required field.
   */
  required: (value: string, fieldName: string = 'This field'): string | null => {
    if (!value || value.trim().length === 0) {
      return `${fieldName} is required`;
    }
    return null;
  },

  /**
   * Validate phone number.
   * 
   * Types:
   * - mobile: +XX XXX XXX XXX (e.g., +48123456789)
   * - landline: XX XX XXX (e.g., 171234567)
   * - internal: XXXX (e.g., 1234)
   */
  phone: (
    value: string,
    type: 'mobile' | 'landline' | 'internal'
  ): string | null => {
    if (!value) return 'Phone number is required';
    
    // Remove spaces and dashes for validation
    const cleaned = value.replace(/[\s-()]/g, '');
    
    if (type === 'mobile') {
      // Must start with + and have 10-15 digits
      if (!/^\+[0-9]{10,15}$/.test(cleaned)) {
        return 'Mobile number must start with + and contain 10-15 digits (e.g., +48123456789)';
      }
    } else if (type === 'landline') {
      // Must have 9-12 digits (no +)
      if (!/^[0-9]{9,12}$/.test(cleaned)) {
        return 'Landline number must contain 9-12 digits (e.g., 171234567)';
      }
    } else if (type === 'internal') {
      // Must have 3-5 digits
      if (!/^[0-9]{3,5}$/.test(cleaned)) {
        return 'Internal extension must contain 3-5 digits (e.g., 1234)';
      }
    }
    
    return null;
  },

  /**
   * Sanitize user input (XSS prevention).
   * 
   * Security: Remove potentially dangerous characters.
   * Note: React auto-escapes by default, but defense in depth!
   */
  sanitize: (value: string): string => {
    return value
      .replace(/<script/gi, '')
      .replace(/<\/script/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+=/gi, '');
  },
};
