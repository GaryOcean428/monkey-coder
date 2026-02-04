/**
 * Type guards and validation helpers for CLI type safety
 */

// Valid task types
export const VALID_TASK_TYPES = [
  'code_generation',
  'code_analysis',
  'code_review',
  'documentation',
  'testing',
  'debugging',
  'refactoring',
  'custom'
] as const;

// Valid personas
export const VALID_PERSONAS = [
  'developer',
  'architect',
  'reviewer',
  'security_analyst',
  'performance_expert',
  'tester',
  'technical_writer',
  'custom'
] as const;

export type TaskType = typeof VALID_TASK_TYPES[number];
export type Persona = typeof VALID_PERSONAS[number];

/**
 * Validates and returns a task type, defaults to 'custom' if invalid
 */
export function validateTaskType(taskType: string): 'code_generation' | 'code_analysis' | 'code_review' | 'documentation' | 'testing' | 'debugging' | 'refactoring' | 'custom' {
  if (VALID_TASK_TYPES.includes(taskType as TaskType)) {
    return taskType as TaskType;
  }
  console.warn(`Invalid task type: ${taskType}, defaulting to 'custom'`);
  return 'custom';
}

/**
 * Validates and returns a persona, defaults to 'developer' if invalid
 */
export function validatePersona(persona: string | undefined): 'developer' | 'architect' | 'reviewer' | 'security_analyst' | 'performance_expert' | 'tester' | 'technical_writer' | 'custom' {
  if (!persona) {
    return 'developer';
  }
  if (VALID_PERSONAS.includes(persona as Persona)) {
    return persona as Persona;
  }
  console.warn(`Invalid persona: ${persona}, defaulting to 'developer'`);
  return 'developer';
}

/**
 * Type guard to check if a string is a valid task type
 */
export function isValidTaskType(taskType: string): taskType is TaskType {
  return VALID_TASK_TYPES.includes(taskType as TaskType);
}

/**
 * Type guard to check if a string is a valid persona
 */
export function isValidPersona(persona: string): persona is Persona {
  return VALID_PERSONAS.includes(persona as Persona);
}
