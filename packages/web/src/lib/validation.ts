/**
 * Form validation utilities and common validation functions
 */

// Email validation with detailed feedback
export function validateEmail(email: string): string | undefined {
  if (!email.trim()) {
    return "Email is required"
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return "Please enter a valid email address"
  }
  
  // Check for common typos - simplified version
  const domain = email.split('@')[1]?.toLowerCase()
  if (domain) {
    if (domain === 'gmai.com' || domain === 'gmailcom') {
      return 'Did you mean gmail.com?'
    }
    if (domain === 'yaho.com' || domain === 'yahooo.com') {
      return 'Did you mean yahoo.com?'
    }
  }
  
  return undefined
}

// Username validation
export function validateUsername(username: string): string | undefined {
  if (!username.trim()) {
    return "Username is required"
  }
  
  if (username.length < 3) {
    return "Username must be at least 3 characters"
  }
  
  if (username.length > 20) {
    return "Username must be less than 20 characters"
  }
  
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return "Username can only contain letters, numbers, and underscores"
  }
  
  // Check for reserved usernames
  const reserved = ['admin', 'root', 'user', 'test', 'null', 'undefined']
  if (reserved.includes(username.toLowerCase())) {
    return "This username is not available"
  }
  
  return undefined
}

// Password validation
export function validatePassword(password: string): string | undefined {
  if (!password) {
    return "Password is required"
  }
  
  if (password.length < 8) {
    return "Password must be at least 8 characters long"
  }
  
  const checks = [
    { test: /[A-Z]/, message: "Include at least one uppercase letter" },
    { test: /[a-z]/, message: "Include at least one lowercase letter" },
    { test: /\d/, message: "Include at least one number" },
    { test: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/, message: "Include at least one special character" }
  ]
  
  for (const check of checks) {
    if (!check.test.test(password)) {
      return check.message
    }
  }
  
  return undefined
}

// Confirm password validation
export function validateConfirmPassword(password: string, confirmPassword: string): string | undefined {
  if (!confirmPassword) {
    return "Please confirm your password"
  }
  
  if (password !== confirmPassword) {
    return "Passwords do not match"
  }
  
  return undefined
}

// Name validation
export function validateName(name: string, fieldName: string = "Name"): string | undefined {
  if (!name.trim()) {
    return `${fieldName} is required`
  }
  
  if (name.trim().length < 2) {
    return `${fieldName} must be at least 2 characters`
  }
  
  if (name.trim().length > 50) {
    return `${fieldName} must be less than 50 characters`
  }
  
  // Check for valid characters (letters, spaces, hyphens, apostrophes)
  if (!/^[a-zA-Z\s\-']+$/.test(name.trim())) {
    return `${fieldName} can only contain letters, spaces, hyphens, and apostrophes`
  }
  
  return undefined
}

// Phone number validation (flexible format)
export function validatePhone(phone: string): string | undefined {
  if (!phone.trim()) {
    return "Phone number is required"
  }
  
  // Remove all non-digit characters
  const digitsOnly = phone.replace(/\D/g, '')
  
  if (digitsOnly.length < 10) {
    return "Phone number must be at least 10 digits"
  }
  
  if (digitsOnly.length > 15) {
    return "Phone number is too long"
  }
  
  return undefined
}

// Subject/title validation
export function validateSubject(subject: string): string | undefined {
  if (!subject.trim()) {
    return "Subject is required"
  }
  
  if (subject.trim().length < 5) {
    return "Subject must be at least 5 characters"
  }
  
  if (subject.trim().length > 100) {
    return "Subject must be less than 100 characters"
  }
  
  return undefined
}

// Message/content validation
export function validateMessage(message: string, minLength: number = 10): string | undefined {
  if (!message.trim()) {
    return "Message is required"
  }
  
  if (message.trim().length < minLength) {
    return `Message must be at least ${minLength} characters`
  }
  
  if (message.trim().length > 2000) {
    return "Message must be less than 2000 characters"
  }
  
  return undefined
}

// Async email availability check (simulate API call)
export async function checkEmailAvailability(email: string): Promise<string | undefined> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 800))
  
  // Simulate some emails being taken
  const takenEmails = ['test@example.com', 'admin@test.com', 'user@demo.com']
  
  if (takenEmails.includes(email.toLowerCase())) {
    return "This email is already registered"
  }
  
  return undefined
}

// Async username availability check (simulate API call)
export async function checkUsernameAvailability(username: string): Promise<string | undefined> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 600))
  
  // Simulate some usernames being taken
  const takenUsernames = ['admin', 'test', 'user', 'demo', 'gary', 'monkey']
  
  if (takenUsernames.includes(username.toLowerCase())) {
    return "This username is not available"
  }
  
  return undefined
}

// Utility to debounce validation functions
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeout: NodeJS.Timeout
  
  return (...args: Parameters<T>): Promise<ReturnType<T>> => {
    return new Promise((resolve) => {
      clearTimeout(timeout)
      timeout = setTimeout(() => {
        resolve(func(...args))
      }, wait)
    })
  }
}

// Form validation state management
export interface ValidationState {
  isValid: boolean
  errors: Record<string, string>
  isValidating: Record<string, boolean>
}

export function createValidationState(): ValidationState {
  return {
    isValid: true,
    errors: {},
    isValidating: {}
  }
}

export function updateValidationState(
  state: ValidationState,
  field: string,
  error?: string,
  isValidating?: boolean
): ValidationState {
  const newErrors = { ...state.errors }
  const newValidating = { ...state.isValidating }
  
  if (error) {
    newErrors[field] = error
  } else {
    delete newErrors[field]
  }
  
  if (isValidating !== undefined) {
    if (isValidating) {
      newValidating[field] = true
    } else {
      delete newValidating[field]
    }
  }
  
  return {
    isValid: Object.keys(newErrors).length === 0,
    errors: newErrors,
    isValidating: newValidating
  }
}