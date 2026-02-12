/**
 * Models utility for fetching and working with AI model data
 */

import { apiFetch, handleApiResponse } from '@/config/api';

export interface ModelInfo {
  name: string;
  provider: string;
  type: string;
  context_length: number;
  input_cost: number;
  output_cost: number;
  capabilities: string[];
  description: string;
  version?: string;
  release_date?: string;
}

export interface ProviderInfo {
  name: string;
  type: string;
  status: string;
  available_models: string[];
  rate_limits: Record<string, any>;
  pricing: Record<string, any>;
  capabilities: string[];
  last_updated: string;
}

export interface ModelsStats {
  totalModels: number;
  providerBreakdown: Record<string, number>;
  modelsByProvider: Record<string, string[]>;
  latestModels: string[];
}

// Hardcoded model data from the backend models.py file
// This is a fallback in case the backend is not available
const FALLBACK_MODEL_REGISTRY = {
  openai: [
    'gpt-5',
    'gpt-5-mini', 
    'gpt-5-nano',
    'gpt-4.1',
    'gpt-4.1-mini',
    'gpt-4.1-vision',
    'o4-mini',
    'o3-pro',
    'o3',
    'o3-mini',
  ],
  anthropic: [
    'claude-sonnet-4-5',
    'claude-opus-4-6',
    'claude-haiku-4-5',
  ],
  google: [
    'gemini-2.5-pro',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
  ],
  grok: [
    'grok-4',
    'grok-3',
    'grok-3-mini',
    'grok-3-mini-fast',
    'grok-3-fast',
    'grok-code-fast-1',
  ],
  groq: [
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'meta-llama/llama-4-maverick-17b-128e-instruct',
    'meta-llama/llama-4-scout-17b-16e-instruct',
    'moonshotai/kimi-k2-instruct',
    'qwen/qwen3-32b',
  ],
};

/**
 * Get available models from the backend API
 */
export async function getAvailableModels(): Promise<Record<string, string[]>> {
  try {
    // Try to fetch from backend first
    const response = await apiFetch('/api/v1/models/available');
    const data = await handleApiResponse<Record<string, string[]>>(response);
    return data;
  } catch (error) {
    console.warn('Failed to fetch models from backend, using fallback data:', error);
    return FALLBACK_MODEL_REGISTRY;
  }
}

/**
 * Calculate models statistics for the landing page
 */
export async function getModelsStats(): Promise<ModelsStats> {
  try {
    const modelsByProvider = await getAvailableModels();
    
    const totalModels = Object.values(modelsByProvider).reduce(
      (sum, models) => sum + models.length, 
      0
    );
    
    const providerBreakdown = Object.fromEntries(
      Object.entries(modelsByProvider).map(([provider, models]) => [
        provider.charAt(0).toUpperCase() + provider.slice(1),
        models.length
      ])
    );

    // Get latest/flagship models from each provider
    const latestModels = [
      'gpt-5', // OpenAI flagship
      'claude-sonnet-4-5', // Anthropic flagship
      'gemini-2.5-pro', // Google flagship
      'grok-4', // xAI flagship
      'llama-3.3-70b-versatile', // Groq popular model
    ];

    return {
      totalModels,
      providerBreakdown,
      modelsByProvider,
      latestModels,
    };
  } catch (error) {
    console.error('Error calculating models stats:', error);
    
    // Fallback calculation
    const totalModels = Object.values(FALLBACK_MODEL_REGISTRY).reduce(
      (sum, models) => sum + models.length, 
      0
    );
    
    return {
      totalModels,
      providerBreakdown: {
        OpenAI: FALLBACK_MODEL_REGISTRY.openai.length,
        Anthropic: FALLBACK_MODEL_REGISTRY.anthropic.length,
        Google: FALLBACK_MODEL_REGISTRY.google.length,
        Grok: FALLBACK_MODEL_REGISTRY.grok.length,
        Groq: FALLBACK_MODEL_REGISTRY.groq.length,
      },
      modelsByProvider: FALLBACK_MODEL_REGISTRY,
      latestModels: ['gpt-5', 'claude-sonnet-4-5', 'gemini-2.5-pro', 'grok-4', 'llama-3.3-70b-versatile'],
    };
  }
}

/**
 * Get provider information
 */
export async function getProviderInfo(): Promise<ProviderInfo[]> {
  try {
    const response = await apiFetch('/api/v1/providers/info');
    const data = await handleApiResponse<ProviderInfo[]>(response);
    return data;
  } catch (error) {
    console.warn('Failed to fetch provider info from backend:', error);
    return [];
  }
}