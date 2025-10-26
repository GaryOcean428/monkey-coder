"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Label } from "./label"
import { Input } from "./input"
import { Check, AlertCircle, Eye, EyeOff } from "lucide-react"

export interface FormFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  success?: boolean
  helperText?: string
  showSuccessIcon?: boolean
  showPasswordToggle?: boolean
  isValidating?: boolean
  onValidation?: (value: string) => Promise<string | undefined> | string | undefined
}

const FormField = React.forwardRef<HTMLInputElement, FormFieldProps>(
  ({ 
    className, 
    label, 
    error, 
    success, 
    helperText, 
    showSuccessIcon = true,
    showPasswordToggle = false,
    isValidating = false,
    onValidation,
    type = "text",
    ...props 
  }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false)
    const [internalError, setInternalError] = React.useState<string>()
    const [isInternalValidating, setIsInternalValidating] = React.useState(false)
    const validateTimeoutRef = React.useRef<NodeJS.Timeout>()

    const finalError = error || internalError
    const finalIsValidating = isValidating || isInternalValidating
    const inputType = showPasswordToggle ? (showPassword ? "text" : "password") : type

    const handleValidation = React.useCallback(async (value: string) => {
      if (!onValidation || !value.trim()) {
        setInternalError(undefined)
        return
      }

      setIsInternalValidating(true)
      try {
        const result = await onValidation(value)
        setInternalError(result)
      } catch (_err) {
        setInternalError("Validation failed")
      } finally {
        setIsInternalValidating(false)
      }
    }, [onValidation])

    const handleChange = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
      props.onChange?.(e)
      
      if (onValidation) {
        // Clear previous timeout
        if (validateTimeoutRef.current) {
          clearTimeout(validateTimeoutRef.current)
        }
        
        // Debounce validation by 500ms
        validateTimeoutRef.current = setTimeout(() => {
          handleValidation(e.target.value)
        }, 500)
      }
    }, [props.onChange, handleValidation])

    React.useEffect(() => {
      return () => {
        if (validateTimeoutRef.current) {
          clearTimeout(validateTimeoutRef.current)
        }
      }
    }, [])

    const getValidationState = () => {
      if (finalIsValidating) return "validating"
      if (finalError) return "error"
      if (success && showSuccessIcon) return "success"
      return "default"
    }

    const validationState = getValidationState()

    return (
      <div className="space-y-2">
        <Label 
          htmlFor={props.id} 
          className={cn(
            "text-sm font-medium leading-none",
            validationState === "error" && "text-destructive",
            validationState === "success" && "text-green-600"
          )}
        >
          {label}
          {props.required && <span className="text-destructive ml-1">*</span>}
        </Label>
        
        <div className="relative">
          <Input
            ref={ref}
            type={inputType}
            className={cn(
              "pr-10",
              validationState === "error" && "border-destructive focus-visible:ring-destructive",
              validationState === "success" && "border-green-500 focus-visible:ring-green-500",
              finalIsValidating && "border-blue-400",
              className
            )}
            onChange={handleChange}
            {...props}
          />
          
          {/* Validation Icons */}
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 space-x-1">
            {showPasswordToggle && (
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-muted-foreground hover:text-foreground transition-colors"
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            )}
            
            {finalIsValidating && (
              <div 
                data-testid="validation-spinner"
                className="animate-spin h-4 w-4 border-2 border-blue-400 border-t-transparent rounded-full" 
              />
            )}
            
            {validationState === "error" && !finalIsValidating && (
              <AlertCircle className="h-4 w-4 text-destructive" data-testid="error-icon" />
            )}
            
            {validationState === "success" && !finalIsValidating && (
              <Check className="h-4 w-4 text-green-600" data-testid="success-icon" />
            )}
          </div>
        </div>

        {/* Helper Text and Error Messages */}
        {(finalError || helperText) && (
          <div className="space-y-1">
            {finalError && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {finalError}
              </p>
            )}
            {!finalError && helperText && (
              <p className="text-sm text-muted-foreground">{helperText}</p>
            )}
          </div>
        )}
      </div>
    )
  }
)
FormField.displayName = "FormField"

export { FormField }