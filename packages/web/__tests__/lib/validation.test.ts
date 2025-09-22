import {
  validateEmail,
  validateUsername,
  validatePassword,
  validateConfirmPassword,
  validateName,
  validatePhone,
  validateSubject,
  validateMessage,
  checkEmailAvailability,
  checkUsernameAvailability,
  debounce,
  createValidationState,
  updateValidationState
} from '../../src/lib/validation'

describe('Validation Functions', () => {
  describe('validateEmail', () => {
    it('returns error for empty email', () => {
      expect(validateEmail('')).toBe('Email is required')
      expect(validateEmail('   ')).toBe('Email is required')
    })

    it('returns error for invalid email format', () => {
      expect(validateEmail('invalid-email')).toBe('Please enter a valid email address')
      expect(validateEmail('test@')).toBe('Please enter a valid email address')
      expect(validateEmail('@domain.com')).toBe('Please enter a valid email address')
    })

    it('returns undefined for valid email', () => {
      expect(validateEmail('test@example.com')).toBeUndefined()
      expect(validateEmail('user.name@domain.co.uk')).toBeUndefined()
    })

    it('suggests corrections for common domain typos', () => {
      expect(validateEmail('test@gmai.com')).toBe('Did you mean gmail.com?')
      // This test case is invalid email format, so it should fail basic validation
      expect(validateEmail('test@invalidformat')).toBe('Please enter a valid email address')
      expect(validateEmail('test@valid.com')).toBeUndefined()
    })
  })

  describe('validateUsername', () => {
    it('returns error for empty username', () => {
      expect(validateUsername('')).toBe('Username is required')
      expect(validateUsername('   ')).toBe('Username is required')
    })

    it('returns error for too short username', () => {
      expect(validateUsername('ab')).toBe('Username must be at least 3 characters')
    })

    it('returns error for too long username', () => {
      expect(validateUsername('a'.repeat(21))).toBe('Username must be less than 20 characters')
    })

    it('returns error for invalid characters', () => {
      expect(validateUsername('user@name')).toBe('Username can only contain letters, numbers, and underscores')
      expect(validateUsername('user-name')).toBe('Username can only contain letters, numbers, and underscores')
      expect(validateUsername('user name')).toBe('Username can only contain letters, numbers, and underscores')
    })

    it('returns error for reserved usernames', () => {
      expect(validateUsername('admin')).toBe('This username is not available')
      expect(validateUsername('root')).toBe('This username is not available')
      expect(validateUsername('ADMIN')).toBe('This username is not available')
    })

    it('returns undefined for valid username', () => {
      expect(validateUsername('validuser')).toBeUndefined()
      expect(validateUsername('user_123')).toBeUndefined()
      expect(validateUsername('TestUser')).toBeUndefined()
    })
  })

  describe('validatePassword', () => {
    it('returns error for empty password', () => {
      expect(validatePassword('')).toBe('Password is required')
    })

    it('returns error for too short password', () => {
      expect(validatePassword('1234567')).toBe('Password must be at least 8 characters long')
    })

    it('returns error for missing uppercase letter', () => {
      expect(validatePassword('password123!')).toBe('Include at least one uppercase letter')
    })

    it('returns error for missing lowercase letter', () => {
      expect(validatePassword('PASSWORD123!')).toBe('Include at least one lowercase letter')
    })

    it('returns error for missing number', () => {
      expect(validatePassword('Password!')).toBe('Include at least one number')
    })

    it('returns error for missing special character', () => {
      expect(validatePassword('Password123')).toBe('Include at least one special character')
    })

    it('returns undefined for valid password', () => {
      expect(validatePassword('Password123!')).toBeUndefined()
      expect(validatePassword('StrongP@ssw0rd')).toBeUndefined()
    })
  })

  describe('validateConfirmPassword', () => {
    it('returns error for empty confirm password', () => {
      expect(validateConfirmPassword('password', '')).toBe('Please confirm your password')
    })

    it('returns error for mismatched passwords', () => {
      expect(validateConfirmPassword('password1', 'password2')).toBe('Passwords do not match')
    })

    it('returns undefined for matching passwords', () => {
      expect(validateConfirmPassword('password', 'password')).toBeUndefined()
    })
  })

  describe('validateName', () => {
    it('returns error for empty name', () => {
      expect(validateName('')).toBe('Name is required')
      expect(validateName('   ')).toBe('Name is required')
    })

    it('returns error for too short name', () => {
      expect(validateName('A')).toBe('Name must be at least 2 characters')
    })

    it('returns error for too long name', () => {
      expect(validateName('A'.repeat(51))).toBe('Name must be less than 50 characters')
    })

    it('returns error for invalid characters', () => {
      expect(validateName('John123')).toBe('Name can only contain letters, spaces, hyphens, and apostrophes')
      expect(validateName('John@Doe')).toBe('Name can only contain letters, spaces, hyphens, and apostrophes')
    })

    it('returns undefined for valid names', () => {
      expect(validateName('John Doe')).toBeUndefined()
      expect(validateName("O'Connor")).toBeUndefined()
      expect(validateName('Mary-Jane')).toBeUndefined()
    })

    it('uses custom field name in error messages', () => {
      expect(validateName('', 'First Name')).toBe('First Name is required')
      expect(validateName('A', 'Last Name')).toBe('Last Name must be at least 2 characters')
    })
  })

  describe('validatePhone', () => {
    it('returns error for empty phone', () => {
      expect(validatePhone('')).toBe('Phone number is required')
    })

    it('returns error for too short phone', () => {
      expect(validatePhone('123')).toBe('Phone number must be at least 10 digits')
    })

    it('returns error for too long phone', () => {
      expect(validatePhone('1'.repeat(16))).toBe('Phone number is too long')
    })

    it('returns undefined for valid phone numbers', () => {
      expect(validatePhone('1234567890')).toBeUndefined()
      expect(validatePhone('(123) 456-7890')).toBeUndefined()
      expect(validatePhone('+1-123-456-7890')).toBeUndefined()
    })
  })

  describe('validateSubject', () => {
    it('returns error for empty subject', () => {
      expect(validateSubject('')).toBe('Subject is required')
    })

    it('returns error for too short subject', () => {
      expect(validateSubject('Hi')).toBe('Subject must be at least 5 characters')
    })

    it('returns error for too long subject', () => {
      expect(validateSubject('A'.repeat(101))).toBe('Subject must be less than 100 characters')
    })

    it('returns undefined for valid subject', () => {
      expect(validateSubject('Hello there')).toBeUndefined()
    })
  })

  describe('validateMessage', () => {
    it('returns error for empty message', () => {
      expect(validateMessage('')).toBe('Message is required')
    })

    it('returns error for too short message', () => {
      expect(validateMessage('Hi')).toBe('Message must be at least 10 characters')
    })

    it('returns error for too long message', () => {
      expect(validateMessage('A'.repeat(2001))).toBe('Message must be less than 2000 characters')
    })

    it('returns undefined for valid message', () => {
      expect(validateMessage('This is a valid message that is long enough')).toBeUndefined()
    })

    it('respects custom minimum length', () => {
      expect(validateMessage('Short', 20)).toBe('Message must be at least 20 characters')
    })
  })

  describe('Async validation functions', () => {
    describe('checkEmailAvailability', () => {
      it('returns error for taken emails', async () => {
        const result = await checkEmailAvailability('test@example.com')
        expect(result).toBe('This email is already registered')
      })

      it('returns undefined for available emails', async () => {
        const result = await checkEmailAvailability('available@example.com')
        expect(result).toBeUndefined()
      })
    })

    describe('checkUsernameAvailability', () => {
      it('returns error for taken usernames', async () => {
        const result = await checkUsernameAvailability('admin')
        expect(result).toBe('This username is not available')
      })

      it('returns undefined for available usernames', async () => {
        const result = await checkUsernameAvailability('availableuser')
        expect(result).toBeUndefined()
      })
    })
  })

  describe('debounce', () => {
    it('debounces function calls', async () => {
      const mockFn = jest.fn().mockReturnValue('result')
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn('arg1')
      debouncedFn('arg2')
      debouncedFn('arg3')

      expect(mockFn).not.toHaveBeenCalled()

      await new Promise(resolve => setTimeout(resolve, 150))

      expect(mockFn).toHaveBeenCalledTimes(1)
      expect(mockFn).toHaveBeenCalledWith('arg3')
    })
  })

  describe('Validation state management', () => {
    describe('createValidationState', () => {
      it('creates initial validation state', () => {
        const state = createValidationState()
        expect(state).toEqual({
          isValid: true,
          errors: {},
          isValidating: {}
        })
      })
    })

    describe('updateValidationState', () => {
      it('adds error to state', () => {
        const initialState = createValidationState()
        const newState = updateValidationState(initialState, 'email', 'Invalid email')
        
        expect(newState.isValid).toBe(false)
        expect(newState.errors.email).toBe('Invalid email')
      })

      it('removes error from state', () => {
        const stateWithError = {
          isValid: false,
          errors: { email: 'Invalid email' },
          isValidating: {}
        }
        const newState = updateValidationState(stateWithError, 'email')
        
        expect(newState.isValid).toBe(true)
        expect(newState.errors.email).toBeUndefined()
      })

      it('updates validation state', () => {
        const initialState = createValidationState()
        const newState = updateValidationState(initialState, 'email', undefined, true)
        
        expect(newState.isValidating.email).toBe(true)
      })
    })
  })
})