/**
 * Type definitions for Monkey Coder CLI
 * Provides interfaces for API communication and command handling
 */

export interface ExecuteRequest {
  task_id?: string;
  task_type:
    | 'code_generation'
    | 'code_analysis'
    | 'code_review'
    | 'documentation'
    | 'testing'
    | 'debugging'
    | 'refactoring'
    | 'custom';
  prompt: string;
  files?: Array<{
    path: string;
    content: string;
    type?: string;
  }>;
  context: {
    user_id: string;
    session_id?: string;
    workspace_id?: string;
    environment?: string;
    timeout?: number;
    max_tokens?: number;
    temperature?: number;
  };
  persona_config: {
    persona:
      | 'developer'
      | 'architect'
      | 'reviewer'
      | 'security_analyst'
      | 'performance_expert'
      | 'tester'
      | 'technical_writer'
      | 'custom';
    slash_commands?: string[];
    context_window?: number;
    use_markdown_spec?: boolean;
    custom_instructions?: string;
  };
  monkey1_config?: {
    agent_count?: number;
    coordination_strategy?: string;
    consensus_threshold?: number;
    enable_reflection?: boolean;
    max_iterations?: number;
  };
  orchestration_config?: {
    parallel_futures?: boolean;
    collapse_strategy?: string;
    quantum_coherence?: number;
    execution_branches?: number;
    uncertainty_threshold?: number;
  };
  preferred_providers?: string[];
  model_preferences?: Record<string, string>;
  model_config?: Record<string, any>;
}

export interface ExecuteResponse {
  execution_id: string;
  task_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  result?: {
    result: any;
    metadata: Record<string, any>;
    artifacts: Array<Record<string, any>>;
    confidence_score: number;
    quantum_collapse_info: Record<string, any>;
  };
  error?: string;
  created_at: string;
  completed_at?: string;
  usage?: {
    tokens_used: number;
    tokens_input: number;
    tokens_output: number;
    provider_breakdown: Record<string, number>;
    cost_estimate: number;
    execution_time: number;
  };
  execution_time?: number;
  persona_routing: Record<string, any>;
  monkey1_orchestration: Record<string, any>;
  orchestration_execution: Record<string, any>;
}

export interface CommandOptions {
  output?: string;
  language?: string;
  type?: string;
  persona?: string;
  model?: string;
  provider?: string;
  temperature?: number;
  timeout?: number;
  verbose?: boolean;
  config?: string;
  apiKey?: string;
  baseUrl?: string;
  stream?: boolean;
  framework?: string;
  // Session management options
  continue?: boolean;
  resume?: string;
  session?: string;
  newSession?: boolean;
}

export interface ConfigFile {
  apiKey?: string;
  baseUrl?: string;
  defaultPersona?: string;
  defaultModel?: string;
  defaultProvider?: string;
  defaultTemperature?: number;
  defaultTimeout?: number;
  // Authentication fields
  refreshToken?: string;
  userEmail?: string;
  userName?: string;
  userCredits?: string;
  subscriptionTier?: string;
  showSplash?: boolean;
  preferences?: {
    [key: string]: any;
  };
}

export interface StreamEvent {
  type: 'start' | 'progress' | 'result' | 'error' | 'complete';
  data?: any;
  progress?: {
    step: string;
    percentage?: number;
    metadata?: Record<string, any>;
  };
  error?: {
    message: string;
    code?: string;
  };
}
