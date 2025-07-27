/**
 * Monkey Coder SDK - TypeScript/JavaScript client
 */

import axios, { AxiosInstance } from 'axios';

export interface GenerationRequest {
  prompt: string;
  language?: string;
  maxLength?: number;
  temperature?: number;
}

export interface GenerationResponse {
  code: string;
  language: string;
  metadata?: Record<string, any>;
}

export interface AnalysisRequest {
  code: string;
  language?: string;
  analysisType?: 'quality' | 'security' | 'performance';
}

export interface AnalysisResponse {
  score: number;
  issues: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
    line?: number;
  }>;
  suggestions: string[];
}

export class MonkeyCoderClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000', apiKey?: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
      },
    });
  }

  async generateCode(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await this.client.post('/generate', request);
    return response.data;
  }

  async analyzeCode(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await this.client.post('/analyze', request);
    return response.data;
  }

  async health(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export default MonkeyCoderClient;
