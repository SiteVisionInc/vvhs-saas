// frontend/src/services/api.ts
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';
import { LoginRequest, TokenResponse, User, Volunteer, Event } from '../types';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    // Prefer relative API path to always use Caddy's /api proxy in prod
    const baseURL =
      process.env.NODE_ENV === 'development' ? 'http://localhost:8000/api' : '/api';

    this.client = axios.create({
      baseURL,
      headers: { 'Content-Type': 'application/json' },
      withCredentials: false,
    });

    // ✅ Load token immediately so first request after reload has auth
    const saved = localStorage.getItem('token');
    if (saved) {
      this.token = saved;
      this.client.defaults.headers.common['Authorization'] = `Bearer ${saved}`;
    }

    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      if (this.token) {
        // headers may be AxiosHeaders or undefined; normalize it
        if (!config.headers) {
          config.headers = {} as any;
        }
        // Works for both AxiosHeaders and plain object
        (config.headers as any).Authorization = `Bearer ${this.token}`;
      }
      return config;
    });
	
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error?.response?.status === 401) {
          // Optional: try one refresh here using localStorage.getItem('refresh_token')
          this.clearToken();
          // Use your router navigation if available
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
    delete this.client.defaults.headers.common['Authorization'];
  }

  loadToken() {
    const token = localStorage.getItem('token');
    if (token) this.setToken(token);
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const res = await this.client.post<TokenResponse>('/v1/auth/login', data);
    this.setToken(res.data.access_token);
    localStorage.setItem('refresh_token', res.data.refresh_token ?? '');
    return res.data;
  }

  async getCurrentUser(): Promise<User> {
    const res = await this.client.get<User>('/v1/users/me');
    return res.data;
  }

  async logout() {
    try {
      await this.client.post('/v1/auth/logout');
    } finally {
      this.clearToken();
    }
  }

  async getVolunteers(): Promise<Volunteer[]> {
    const res = await this.client.get<{ total: number; items: Volunteer[] }>('/v1/volunteers/');
    return res.data.items;
  }

  async getVolunteer(id: string): Promise<Volunteer> {
    const res = await this.client.get<Volunteer>(`/v1/volunteers/${id}`);
    return res.data;
  }

  async createVolunteer(data: Partial<Volunteer>): Promise<Volunteer> {
    const res = await this.client.post<Volunteer>('/v1/volunteers/', data);
    return res.data;
  }

  async updateVolunteer(id: string, data: Partial<Volunteer>): Promise<Volunteer> {
    const res = await this.client.put<Volunteer>(`/v1/volunteers/${id}`, data);
    return res.data;
  }

  async deleteVolunteer(id: string): Promise<void> {
    await this.client.delete(`/v1/volunteers/${id}`);
  }

  async getEvents(): Promise<Event[]> {
    const res = await this.client.get<Event[]>('/v1/events/');
    return res.data;
  }

}

export const api = new ApiService();
