// frontend/src/services/api.ts
import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';
import { LoginRequest, TokenResponse, User, Volunteer, Event } from '../types';
//import type { InternalAxiosRequestConfig } from 'axios';

class ApiService {
  public client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      // Caddy proxies /api/* to the backend
      baseURL: '/api',
      headers: { 'Content-Type': 'application/json' },
      withCredentials: false,
    });

    // Load any existing token into default headers on startup
    this.loadToken();

this.client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      // Axios v1 headers can be a Headers-like object with .set()
      const h: any = config.headers;
      if (typeof h?.set === 'function') {
        h.set('Authorization', `Bearer ${token}`);
      } else {
        (config.headers as any)['Authorization'] = `Bearer ${token}`;
      }
    }
	
	console.debug(
      `→ ${String(config.method).toUpperCase()} ${config.baseURL ?? ''}${config.url} | token:${token ? 'yes' : 'no'}`
    );
	
    return config;
  },
  (error) => Promise.reject(error)
);


    // Handle 401 responses (optionally disable during debugging)
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
		    console.debug('✗ Response error', {
              status: error.response?.status,
               url: error.config?.url,
               data: error.response?.data,
            });
        if (error.response?.status === 401 && !String(error.config?.url).includes('/auth/login')) {
          // NOTE: while debugging 401s, you can comment these two lines
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          delete this.client.defaults.headers.common['Authorization'];

          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // ----- Token helpers -----
  setToken(token: string) {
    localStorage.setItem('token', token);
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  loadToken(): string | null {
    const token = localStorage.getItem('token');
    if (token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    return token;
  }

  // ----- Auth -----
  async login(data: LoginRequest): Promise<TokenResponse> {
    const res = await this.client.post<TokenResponse>('/v1/auth/login', data);

    if (res.data.access_token) {
      localStorage.setItem('token', res.data.access_token);
      if (res.data.refresh_token) {
        localStorage.setItem('refresh_token', res.data.refresh_token);
      }
	  
      // <-- add this line so the next request immediately carries the header
      this.client.defaults.headers.common['Authorization'] =
        `Bearer ${res.data.access_token}`;
  }

  return res.data;
}

  async logout(): Promise<void> {
    try {
      await this.client.post('/v1/auth/logout');
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      delete this.client.defaults.headers.common['Authorization'];
    }
  }

  // ----- Users -----
  async getCurrentUser(): Promise<User> {
    const res = await this.client.get<User>('/v1/users/me');
    return res.data;
  }

  // ----- Volunteers -----
  async getVolunteers(): Promise<Volunteer[]> {
    const res = await this.client.get<any>('/v1/volunteers/');
    return res.data?.items ?? res.data ?? [];
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

  // ----- Events -----
  async getEvents(): Promise<Event[]> {
    const res = await this.client.get<any>('/v1/events/');
    return Array.isArray(res.data) ? res.data : res.data?.items ?? [];
  }
}

export const api = new ApiService();
