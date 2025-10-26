"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { CheckCircle, AlertCircle, Loader2, Info } from "lucide-react"

export interface FormStatusProps {
  status: "idle" | "submitting" | "success" | "error"
  message?: string
  details?: string
  className?: string
  autoHideSuccess?: number // Auto-hide success message after X milliseconds
  onStatusChange?: (status: FormStatusProps["status"]) => void
}

export function FormStatus({ 
  status, 
  message, 
  details,
  className,
  autoHideSuccess = 0,
  onStatusChange
}: FormStatusProps) {
  const [isVisible, setIsVisible] = React.useState(true)

  React.useEffect(() => {
    if (status === "success" && autoHideSuccess > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        onStatusChange?.("idle")
      }, autoHideSuccess)
      
      return () => clearTimeout(timer)
    }
    
    if (status !== "idle") {
      setIsVisible(true)
    }
  }, [status, autoHideSuccess, onStatusChange])

  if (status === "idle" || !isVisible) {
    return null
  }

  const getStatusConfig = () => {
    switch (status) {
      case "submitting":
        return {
          icon: Loader2,
          iconClassName: "h-4 w-4 animate-spin text-blue-600",
          containerClassName: "border-blue-200 bg-blue-50 text-blue-800",
          defaultMessage: "Processing your request...",
          testId: "loading-spinner"
        }
      case "success":
        return {
          icon: CheckCircle,
          iconClassName: "h-4 w-4 text-green-600",
          containerClassName: "border-green-200 bg-green-50 text-green-800",
          defaultMessage: "Success! Your request has been completed.",
          testId: "success-icon"
        }
      case "error":
        return {
          icon: AlertCircle,
          iconClassName: "h-4 w-4 text-red-600",
          containerClassName: "border-red-200 bg-red-50 text-red-800",
          defaultMessage: "An error occurred. Please try again.",
          testId: "error-icon"
        }
      default:
        return {
          icon: Info,
          iconClassName: "h-4 w-4 text-blue-600",
          containerClassName: "border-blue-200 bg-blue-50 text-blue-800",
          defaultMessage: "",
          testId: "info-icon"
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon
  const displayMessage = message || config.defaultMessage

  return (
    <div
      className={cn(
        "rounded-lg border p-4 transition-all duration-300 ease-in-out",
        config.containerClassName,
        className
      )}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <Icon className={config.iconClassName} data-testid={config.testId} />
        
        <div className="flex-1 space-y-1">
          {displayMessage && (
            <p className="text-sm font-medium">
              {displayMessage}
            </p>
          )}
          
          {details && (
            <p className="text-sm opacity-80">
              {details}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// Hook for managing form status state
export function useFormStatus() {
  const [status, setStatus] = React.useState<FormStatusProps["status"]>("idle")
  const [message, setMessage] = React.useState<string>()
  const [details, setDetails] = React.useState<string>()

  const updateStatus = React.useCallback((
    newStatus: FormStatusProps["status"],
    newMessage?: string,
    newDetails?: string
  ) => {
    setStatus(newStatus)
    setMessage(newMessage)
    setDetails(newDetails)
  }, [])

  const setSubmitting = React.useCallback((message?: string) => {
    updateStatus("submitting", message)
  }, [updateStatus])

  const setSuccess = React.useCallback((message?: string, details?: string) => {
    updateStatus("success", message, details)
  }, [updateStatus])

  const setError = React.useCallback((message?: string, details?: string) => {
    updateStatus("error", message, details)
  }, [updateStatus])

  const reset = React.useCallback(() => {
    updateStatus("idle")
  }, [updateStatus])

  return {
    status,
    message, 
    details,
    setSubmitting,
    setSuccess,
    setError,
    reset,
    updateStatus
  }
}