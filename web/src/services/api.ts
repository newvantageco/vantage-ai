/**
 * API Service
 * Handles all API calls to the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
const MOCK_MODE = process.env.NODE_ENV === 'development' || process.env.NEXT_PUBLIC_DEV_MODE === 'true';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiService {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = this.getToken();
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {

    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.detail || `HTTP ${response.status}`,
          response.status,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0
      );
    }
  }

  private getMockData(endpoint: string): any {
    // Simulate API delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(this.generateMockResponse(endpoint));
      }, 100);
    });
  }

  private generateMockResponse(endpoint: string): any {
    // Dashboard stats
    if (endpoint.includes('/dashboard/stats')) {
      return {
        kpis: [
          { title: 'Total Posts', value: '1,234', change: '+12%', trend: 'up', icon: 'posts', color: 'blue' },
          { title: 'Engagement Rate', value: '8.5%', change: '+2.3%', trend: 'up', icon: 'heart', color: 'red' },
          { title: 'Reach', value: '45.2K', change: '+18%', trend: 'up', icon: 'users', color: 'green' },
          { title: 'AI Generated', value: '567', change: '+25%', trend: 'up', icon: 'brain', color: 'purple' }
        ],
        recent_content: [
          { id: 1, content: 'Check out our latest product launch! 🚀', platforms: ['facebook', 'instagram'], status: 'published', created_at: '2024-01-15T10:30:00Z' },
          { id: 2, content: 'Behind the scenes content creation magic ✨', platforms: ['linkedin'], status: 'scheduled', created_at: '2024-01-15T09:15:00Z' }
        ],
        upcoming_schedules: [],
        platform_stats: [],
        ai_usage: { tokens_used: 15420, cost_usd: 2.85, generations_count: 89 },
        limits: {
          posts: { current: 45, limit: 100, percentage: 45 },
          ai_generations: { current: 89, limit: 200, percentage: 44.5 }
        }
      };
    }

    // AI Content Generation
    if (endpoint.includes('/content/ai/generate')) {
      return {
        content: '🚀 Excited to share our latest innovation! This breakthrough technology will transform how you work and create. Join us on this incredible journey! #Innovation #Technology #Future',
        content_type: 'social_post',
        platform: 'facebook',
        generated_at: new Date().toISOString(),
        tokens_used: 45,
        cost_usd: 0.003
      };
    }

    // Content list
    if (endpoint.includes('/content/list')) {
      return {
        items: [
          {
            id: 1,
            content: 'Amazing product launch announcement! 🎉',
            platforms: ['facebook', 'instagram'],
            content_type: 'post',
            status: 'published',
            created_at: '2024-01-15T10:30:00Z',
            hashtags: ['#launch', '#product'],
            author_id: 1,
            organization_id: 1
          },
          {
            id: 2,
            content: 'Behind the scenes of our creative process',
            platforms: ['linkedin'],
            content_type: 'post', 
            status: 'draft',
            created_at: '2024-01-15T09:15:00Z',
            hashtags: ['#BTS', '#creative'],
            author_id: 1,
            organization_id: 1
          }
        ],
        total: 2,
        page: 1,
        per_page: 10,
        has_next: false,
        has_prev: false
      };
    }

    // Feature access
    if (endpoint.includes('/features/access')) {
      return {
        plan: 'growth',
        features: {
          ai_generations: { enabled: true, limit: 1000, used: 89 },
          social_platforms: { enabled: true, limit: 6, used: 3 },
          team_members: { enabled: true, limit: 10, used: 2 },
          storage_gb: { enabled: true, limit: 25, used: 5.2 },
          analytics: { enabled: true },
          automation: { enabled: true }
        }
      };
    }

    // Analytics
    if (endpoint.includes('/analytics')) {
      return {
        metrics: {
          impressions: { value: 125430, change: 15.2 },
          engagement: { value: 8.7, change: 2.4 },
          clicks: { value: 2340, change: -5.1 },
          reach: { value: 45200, change: 18.3 }
        },
        platforms: {
          facebook: { posts: 15, engagement: 9.2, reach: 18500 },
          instagram: { posts: 20, engagement: 8.5, reach: 15200 },
          linkedin: { posts: 8, engagement: 7.8, reach: 11500 }
        },
        timeline: Array.from({ length: 7 }, (_, i) => ({
          date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          impressions: Math.floor(Math.random() * 20000) + 10000,
          engagement: Math.floor(Math.random() * 1000) + 500,
          clicks: Math.floor(Math.random() * 400) + 100
        })).reverse()
      };
    }

    // Authentication endpoints
    if (endpoint.includes('/auth/simple/login')) {
      return {
        access_token: 'mock-jwt-token-12345',
        refresh_token: 'mock-refresh-token-67890',
        user: {
          id: 1,
          email: 'demo@vantage.ai',
          name: 'Demo User',
          organization_id: 1,
          plan: 'growth'
        }
      };
    }

    if (endpoint.includes('/auth/simple/validate')) {
      return {
        id: 1,
        email: 'demo@vantage.ai',
        name: 'Demo User',
        organization_id: 1,
        organization_name: 'Demo Organization',
        plan: 'growth',
        verified: true,
        created_at: '2024-01-01T00:00:00Z'
      };
    }

    // Billing endpoints
    if (endpoint.includes('/billing/status')) {
      return {
        plan: 'growth',
        status: 'active',
        subscription_id: 'sub_mock123',
        current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        usage: {
          posts: { current: 45, limit: 100 },
          ai_generations: { current: 89, limit: 1000 },
          team_members: { current: 2, limit: 10 }
        }
      };
    }

    if (endpoint.includes('/billing/plans')) {
      return [
        { id: 'starter', name: 'Starter', price: 29, features: ['3 platforms', '200 AI generations', '2 team members'] },
        { id: 'growth', name: 'Growth', price: 79, features: ['6 platforms', '1000 AI generations', '10 team members'] },
        { id: 'pro', name: 'Pro', price: 199, features: ['Unlimited platforms', 'Unlimited AI', '50 team members'] }
      ];
    }

    // Integrations
    if (endpoint.includes('/integrations')) {
      return [
        { platform: 'facebook', connected: true, account: 'Demo Company Page', status: 'active' },
        { platform: 'instagram', connected: true, account: '@democompany', status: 'active' },
        { platform: 'linkedin', connected: false, account: null, status: 'disconnected' },
        { platform: 'google_business', connected: false, account: null, status: 'disconnected' }
      ];
    }

    // Health check
    if (endpoint.includes('/health')) {
      return { status: 'ok', timestamp: new Date().toISOString() };
    }

    // Default mock response
    return { 
      success: true, 
      message: 'Mock data response',
      timestamp: new Date().toISOString(),
      endpoint 
    };
  }

  // Content Creation API
  async createContent(data: {
    content: string;
    platforms: string[];
    content_type?: string;
    scheduled_date?: string;
    media_urls?: string[];
    hashtags?: string[];
    mentions?: string[];
    brand_guide_id?: number;
    locale?: string;
  }) {
    return this.request('/api/v1/content/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getContentList(params: {
    page?: number;
    per_page?: number;
    status?: string;
    content_type?: string;
  } = {}) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    
    const response = await this.request(`/api/v1/content/list?${searchParams.toString()}`);
    
    // Transform the response to match the expected format
    return {
      items: response.content_items || [],
      total: response.total || 0,
      page: response.page || 1,
      per_page: response.size || 20,
      has_next: response.has_more || false,
      has_prev: (response.page || 1) > 1
    };
  }

  async updateContent(contentId: number, data: any) {
    return this.request(`/api/v1/content/${contentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteContent(contentId: number) {
    return this.request(`/api/v1/content/${contentId}`, {
      method: 'DELETE',
    });
  }

  async generateAIContent(data: {
    prompt: string;
    content_type?: string;
    brand_voice?: string;
    platform?: string;
    locale?: string;
  }) {
    return this.request('/api/v1/content/ai/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getContentStats() {
    return this.request('/api/v1/content/stats');
  }

  // Dashboard API
  async getDashboardStats() {
    return this.request('/api/v1/dashboard');
  }

  async getRecentContent(limit: number = 10) {
    return this.request(`/api/v1/dashboard/content/recent?limit=${limit}`);
  }

  async getAnalyticsSummary(days: number = 30) {
    return this.request(`/api/v1/dashboard/analytics/summary?days=${days}`);
  }

  async getSystemHealth() {
    return this.request('/api/v1/dashboard/health');
  }

  // Authentication API
  async login(email: string, password: string) {
    const response = await this.request('/api/v1/auth/simple/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (response.access_token) {
      this.token = response.access_token;
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', response.access_token);
      }
    }
    
    return response;
  }

  async validateToken(token: string) {
    const response = await this.request('/api/v1/auth/simple/validate', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
    
    return response;
  }

  async logout() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  async getCurrentUser() {
    // Return mock user in mock mode
    if (MOCK_MODE) {
      return {
        id: 1,
        email: 'demo@vantage.ai',
        name: 'Demo User',
        organization_id: 1,
        organization_name: 'Demo Organization',
        plan: 'growth',
        verified: true,
        created_at: '2024-01-01T00:00:00Z'
      };
    }

    if (!this.token) {
      throw new Error('No authentication token available');
    }
    return this.validateToken(this.token);
  }

  // Billing API
  async getBillingStatus() {
    return this.request('/api/v1/billing/status');
  }

  async getAvailablePlans() {
    return this.request('/api/v1/billing/plans');
  }

  async createCheckoutSession(priceId: string) {
    return this.request('/api/v1/billing/checkout', {
      method: 'POST',
      body: JSON.stringify({ price_id: priceId }),
    });
  }

  // Integrations API
  async getIntegrations() {
    return this.request('/api/v1/integrations');
  }

  async connectIntegration(platform: string, data: any) {
    return this.request(`/api/v1/integrations/${platform}/connect`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async disconnectIntegration(platform: string) {
    return this.request(`/api/v1/integrations/${platform}/disconnect`, {
      method: 'DELETE',
    });
  }

  // Analytics API
  async getAnalytics(params: {
    start_date?: string;
    end_date?: string;
    platform?: string;
    metric?: string;
  } = {}) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value);
      }
    });
    
    return this.request(`/api/v1/analytics?${searchParams.toString()}`);
  }

  // Feature Access API
  async getFeatureAccess() {
    return this.request('/api/v1/features/access');
  }

  async checkFeatureLimit(feature: string) {
    return this.request(`/api/v1/features/limit/${feature}`);
  }

  // Brave Search Methods
  async searchWeb(params: BraveSearchRequest): Promise<BraveSearchResponse> {
    return this.request('/api/v1/brave-search/web', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  }

  async searchNews(params: BraveSearchRequest): Promise<BraveSearchResponse> {
    return this.request('/api/v1/brave-search/news', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  }

  async searchImages(params: BraveSearchRequest): Promise<BraveSearchResponse> {
    return this.request('/api/v1/brave-search/images', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  }

  async searchVideos(params: BraveSearchRequest): Promise<BraveSearchResponse> {
    return this.request('/api/v1/brave-search/videos', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  }

  async searchLocal(params: BraveSearchRequest & { location: string }): Promise<BraveSearchResponse> {
    return this.request('/api/v1/brave-search/local', {
      method: 'POST',
      body: JSON.stringify(params)
    });
  }

  async getAISummary(summaryKey: string, entityInfo?: boolean, inlineReferences?: boolean): Promise<{ summary: string }> {
    return this.request('/api/v1/brave-search/summary', {
      method: 'POST',
      body: JSON.stringify({
        summary_key: summaryKey,
        entity_info: entityInfo || false,
        inline_references: inlineReferences || false
      })
    });
  }

  // Quick search methods
  async quickWebSearch(query: string, count: number = 10, summary: boolean = false): Promise<BraveSearchResponse> {
    const searchParams = new URLSearchParams({
      q: query,
      count: count.toString(),
      summary: summary.toString()
    });
    return this.request(`/api/v1/brave-search/quick/web?${searchParams.toString()}`);
  }

  async quickNewsSearch(query: string, count: number = 20, freshness: string = 'pd'): Promise<BraveSearchResponse> {
    const searchParams = new URLSearchParams({
      q: query,
      count: count.toString(),
      freshness
    });
    return this.request(`/api/v1/brave-search/quick/news?${searchParams.toString()}`);
  }

  async checkBraveSearchHealth(): Promise<{ status: string; service: string }> {
    return this.request('/api/v1/brave-search/health');
  }

  // Utility methods
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  isAuthenticated(): boolean {
    // Always authenticated in mock mode
    if (MOCK_MODE) {
      return true;
    }
    return !!this.token;
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export types
export interface ContentItem {
  id: string;
  title: string;
  content: string;
  content_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  published_at?: string;
  scheduled_date?: string;
  media_urls?: string[];
  hashtags?: string[];
  mentions?: string[];
  tags?: string[];
  platform_content?: Record<string, string>;
  created_by: string;
  campaign_id?: string;
}

export interface ContentListResponse {
  items: ContentItem[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface KPIMetric {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: string;
  color: string;
}

export interface DashboardStats {
  kpis: KPIMetric[];
  recent_content: any[];
  upcoming_schedules: any[];
  platform_stats: any[];
  ai_usage: {
    tokens_used: number;
    cost_usd: number;
    generations_count: number;
  };
  limits: Record<string, {
    current: number;
    limit: number;
    percentage: number;
  }>;
}

export interface AIContentResponse {
  content: string;
  content_type: string;
  platform?: string;
  generated_at: string;
  tokens_used: number;
  cost_usd: number;
}

// Brave Search Types
export interface BraveSearchResult {
  title: string;
  url: string;
  description: string;
  published_date?: string;
  thumbnail?: string;
  source?: string;
  location?: any;
  price?: string;
  rating?: number;
}

export interface BraveSearchResponse {
  results: BraveSearchResult[];
  total_results: number;
  search_time: number;
  query: string;
  search_type: string;
  summary?: string;
  summary_key?: string;
}

export interface BraveSearchRequest {
  query: string;
  count?: number;
  offset?: number;
  country?: string;
  search_lang?: string;
  ui_lang?: string;
  safesearch?: string;
  summary?: boolean;
  extra_snippets?: boolean;
  freshness?: string;
  spellcheck?: boolean;
}

export { ApiError };
