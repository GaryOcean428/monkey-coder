"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Check, X } from "lucide-react"

export interface PasswordStrengthProps {
  password: string
  showCriteria?: boolean
  className?: string
}

interface PasswordCriteria {
  label: string
  test: (password: string) => boolean
  weight: number
}

const passwordCriteria: PasswordCriteria[] = [
  {
    label: "At least 8 characters",
    test: (password) => password.length >= 8,
    weight: 20,
  },
  {
    label: "Contains uppercase letter",
    test: (password) => /[A-Z]/.test(password),
    weight: 20,
  },
  {
    label: "Contains lowercase letter", 
    test: (password) => /[a-z]/.test(password),
    weight: 20,
  },
  {
    label: "Contains number",
    test: (password) => /\d/.test(password),
    weight: 20,
  },
  {
    label: "Contains special character",
    test: (password) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password),
    weight: 20,
  },
]

export function getPasswordStrength(password: string): {
  score: number
  level: "weak" | "fair" | "good" | "strong"
  percentage: number
} {
  if (!password) {
    return { score: 0, level: "weak", percentage: 0 }
  }

  const metCriteria = passwordCriteria.filter(criteria => criteria.test(password))
  const score = metCriteria.reduce((total, criteria) => total + criteria.weight, 0)
  
  let level: "weak" | "fair" | "good" | "strong"
  if (score <= 40) level = "weak"
  else if (score <= 60) level = "fair"
  else if (score <= 80) level = "good"
  else level = "strong"

  return {
    score,
    level,
    percentage: Math.min(score, 100)
  }
}

export function PasswordStrengthIndicator({ 
  password, 
  showCriteria = true,
  className 
}: PasswordStrengthProps) {
  const { level, percentage } = getPasswordStrength(password)
  
  const strengthColors = {
    weak: "bg-red-500",
    fair: "bg-orange-500", 
    good: "bg-yellow-500",
    strong: "bg-green-500",
  }

  const strengthLabels = {
    weak: "Weak",
    fair: "Fair",
    good: "Good", 
    strong: "Strong",
  }

  if (!password) {
    return null
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Strength Bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium">Password strength</span>
          <span className={cn(
            "text-sm font-medium",
            level === "weak" && "text-red-600",
            level === "fair" && "text-orange-600", 
            level === "good" && "text-yellow-600",
            level === "strong" && "text-green-600"
          )}>
            {strengthLabels[level]}
          </span>
        </div>
        
        <div className="w-full bg-muted rounded-full h-2">
          <div
            className={cn(
              "h-2 rounded-full transition-all duration-300 ease-out",
              strengthColors[level]
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Criteria List */}
      {showCriteria && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">Requirements:</p>
          <ul className="space-y-1">
            {passwordCriteria.map((criteria, index) => {
              const isMet = criteria.test(password)
              return (
                <li
                  key={index}
                  className={cn(
                    "flex items-center gap-2 text-sm transition-colors",
                    isMet ? "text-green-600" : "text-muted-foreground"
                  )}
                >
                  {isMet ? (
                    <Check className="h-3 w-3 text-green-600" data-testid="check-icon" />
                  ) : (
                    <X className="h-3 w-3 text-muted-foreground" data-testid="x-icon" />
                  )}
                  <span className={cn(isMet && "line-through")}>
                    {criteria.label}
                  </span>
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  )
}