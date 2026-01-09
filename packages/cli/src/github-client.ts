/**
 * GitHub API Client
 * Handles GitHub REST API calls with authentication, rate limiting, and pagination
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

export interface GitHubClientOptions {
  token?: string;
  baseURL?: string;
}

export interface GitHubRepository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  language: string | null;
  topics: string[];
  owner: {
    login: string;
    avatar_url: string;
  };
}

export interface GitHubIssue {
  id: number;
  number: number;
  title: string;
  body: string | null;
  state: 'open' | 'closed';
  html_url: string;
  user: {
    login: string;
  };
  labels: Array<{ name: string; color: string }>;
  created_at: string;
  updated_at: string;
}

export interface GitHubRelease {
  id: number;
  tag_name: string;
  name: string | null;
  body: string | null;
  draft: boolean;
  prerelease: boolean;
  created_at: string;
  published_at: string | null;
  html_url: string;
  assets: Array<{
    id: number;
    name: string;
    size: number;
    browser_download_url: string;
    download_count?: number;
  }>;
}

export interface GitHubWorkflow {
  id: number;
  name: string;
  path: string;
  state: 'active' | 'disabled_manually';
  html_url: string;
}

export interface GitHubWorkflowRun {
  id: number;
  name: string;
  head_branch: string;
  status: 'queued' | 'in_progress' | 'completed';
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null;
  html_url: string;
  created_at: string;
  updated_at: string;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: Date;
  used: number;
}

export class GitHubClient {
  private client: AxiosInstance;
  private token?: string;
  private rateLimitInfo?: RateLimitInfo;

  constructor(options: GitHubClientOptions = {}) {
    this.token = options.token || process.env.GITHUB_TOKEN;
    
    this.client = axios.create({
      baseURL: options.baseURL || 'https://api.github.com',
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'monkey-coder-cli',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
      },
      timeout: 30000,
    });

    // Add response interceptor to track rate limits
    this.client.interceptors.response.use(
      (response) => {
        this.updateRateLimitFromHeaders(response.headers);
        return response;
      },
      (error) => {
        if (error.response) {
          this.updateRateLimitFromHeaders(error.response.headers);
          
          // Handle rate limiting
          if (error.response.status === 403 && error.response.headers['x-ratelimit-remaining'] === '0') {
            const resetTime = new Date(parseInt(error.response.headers['x-ratelimit-reset']) * 1000);
            throw new Error(`GitHub API rate limit exceeded. Resets at ${resetTime.toLocaleTimeString()}`);
          }
        }
        throw error;
      }
    );
  }

  private updateRateLimitFromHeaders(headers: any): void {
    if (headers['x-ratelimit-limit']) {
      this.rateLimitInfo = {
        limit: parseInt(headers['x-ratelimit-limit']),
        remaining: parseInt(headers['x-ratelimit-remaining']),
        reset: new Date(parseInt(headers['x-ratelimit-reset']) * 1000),
        used: parseInt(headers['x-ratelimit-used'] || '0'),
      };
    }
  }

  /**
   * Get current rate limit information
   */
  getRateLimitInfo(): RateLimitInfo | undefined {
    return this.rateLimitInfo;
  }

  /**
   * Search repositories
   */
  async searchRepositories(query: string, options: {
    sort?: 'stars' | 'forks' | 'updated';
    order?: 'asc' | 'desc';
    per_page?: number;
    page?: number;
  } = {}): Promise<{ items: GitHubRepository[]; total_count: number }> {
    const response = await this.client.get('/search/repositories', {
      params: {
        q: query,
        sort: options.sort,
        order: options.order,
        per_page: options.per_page || 30,
        page: options.page || 1,
      },
    });
    return response.data;
  }

  /**
   * Search code
   */
  async searchCode(query: string, options: {
    sort?: 'indexed';
    order?: 'asc' | 'desc';
    per_page?: number;
    page?: number;
  } = {}): Promise<{ items: any[]; total_count: number }> {
    const response = await this.client.get('/search/code', {
      params: {
        q: query,
        sort: options.sort,
        order: options.order,
        per_page: options.per_page || 30,
        page: options.page || 1,
      },
    });
    return response.data;
  }

  /**
   * Search issues and pull requests
   */
  async searchIssues(query: string, options: {
    sort?: 'comments' | 'created' | 'updated';
    order?: 'asc' | 'desc';
    per_page?: number;
    page?: number;
  } = {}): Promise<{ items: GitHubIssue[]; total_count: number }> {
    const response = await this.client.get('/search/issues', {
      params: {
        q: query,
        sort: options.sort,
        order: options.order,
        per_page: options.per_page || 30,
        page: options.page || 1,
      },
    });
    return response.data;
  }

  /**
   * List releases for a repository
   */
  async listReleases(owner: string, repo: string, options: {
    per_page?: number;
    page?: number;
  } = {}): Promise<GitHubRelease[]> {
    const response = await this.client.get(`/repos/${owner}/${repo}/releases`, {
      params: {
        per_page: options.per_page || 30,
        page: options.page || 1,
      },
    });
    return response.data;
  }

  /**
   * Get a specific release by tag
   */
  async getReleaseByTag(owner: string, repo: string, tag: string): Promise<GitHubRelease> {
    const response = await this.client.get(`/repos/${owner}/${repo}/releases/tags/${tag}`);
    return response.data;
  }

  /**
   * Get the latest release
   */
  async getLatestRelease(owner: string, repo: string): Promise<GitHubRelease> {
    const response = await this.client.get(`/repos/${owner}/${repo}/releases/latest`);
    return response.data;
  }

  /**
   * Create a release
   */
  async createRelease(owner: string, repo: string, data: {
    tag_name: string;
    name?: string;
    body?: string;
    draft?: boolean;
    prerelease?: boolean;
    target_commitish?: string;
  }): Promise<GitHubRelease> {
    const response = await this.client.post(`/repos/${owner}/${repo}/releases`, data);
    return response.data;
  }

  /**
   * Delete a release
   */
  async deleteRelease(owner: string, repo: string, releaseId: number): Promise<void> {
    await this.client.delete(`/repos/${owner}/${repo}/releases/${releaseId}`);
  }

  /**
   * List workflows for a repository
   */
  async listWorkflows(owner: string, repo: string, options: {
    per_page?: number;
    page?: number;
  } = {}): Promise<{ workflows: GitHubWorkflow[]; total_count: number }> {
    const response = await this.client.get(`/repos/${owner}/${repo}/actions/workflows`, {
      params: {
        per_page: options.per_page || 30,
        page: options.page || 1,
      },
    });
    return response.data;
  }

  /**
   * Get a specific workflow
   */
  async getWorkflow(owner: string, repo: string, workflowId: string | number): Promise<GitHubWorkflow> {
    const response = await this.client.get(`/repos/${owner}/${repo}/actions/workflows/${workflowId}`);
    return response.data;
  }

  /**
   * List workflow runs
   */
  async listWorkflowRuns(owner: string, repo: string, workflowId?: string | number, options: {
    status?: 'queued' | 'in_progress' | 'completed';
    branch?: string;
    per_page?: number;
    page?: number;
  } = {}): Promise<{ workflow_runs: GitHubWorkflowRun[]; total_count: number }> {
    const endpoint = workflowId
      ? `/repos/${owner}/${repo}/actions/workflows/${workflowId}/runs`
      : `/repos/${owner}/${repo}/actions/runs`;
    
    const response = await this.client.get(endpoint, {
      params: {
        status: options.status,
        branch: options.branch,
        per_page: options.per_page || 30,
        page: options.page || 1,
      },
    });
    return response.data;
  }

  /**
   * Trigger a workflow
   */
  async triggerWorkflow(owner: string, repo: string, workflowId: string | number, data: {
    ref: string;
    inputs?: Record<string, string>;
  }): Promise<void> {
    await this.client.post(`/repos/${owner}/${repo}/actions/workflows/${workflowId}/dispatches`, data);
  }

  /**
   * Get workflow run logs
   */
  async getWorkflowRunLogs(owner: string, repo: string, runId: number): Promise<string> {
    const response = await this.client.get(`/repos/${owner}/${repo}/actions/runs/${runId}/logs`, {
      responseType: 'text',
    });
    return response.data;
  }

  /**
   * Get current repository (from git remote)
   */
  async getCurrentRepo(): Promise<{ owner: string; repo: string } | null> {
    try {
      // This would typically parse .git/config or run git commands
      // For now, return null - this will be implemented with Git CLI integration
      return null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Set authentication token
   */
  setToken(token: string): void {
    this.token = token;
    this.client.defaults.headers['Authorization'] = `Bearer ${token}`;
  }
}

// Export a singleton instance
let githubClientInstance: GitHubClient | null = null;

export function getGitHubClient(options?: GitHubClientOptions): GitHubClient {
  if (!githubClientInstance) {
    githubClientInstance = new GitHubClient(options);
  } else if (options?.token) {
    githubClientInstance.setToken(options.token);
  }
  return githubClientInstance;
}
