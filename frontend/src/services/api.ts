import axios, { AxiosInstance } from 'axios';
import { LoginRequest, TokenResponse, User, Volunteer, Event } from '../types';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: 'https://api.vvhs-saas.sitevision.com/api',
      headers: {
        'Content-Type': 'application/json',
      },
	  withCredentials: true,
    });

    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  loadToken() {
    const token = localStorage.getItem('token');
    if (token) {
      this.token = token;
    }
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await this.client.post<TokenResponse>('/v1/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    this.setToken(response.data.access_token);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/v1/auth/me');
    return response.data;
  }

  async logout() {
    this.clearToken();
  }

  async getVolunteers(): Promise<Volunteer[]> {
    const response = await this.client.get<Volunteer[]>('/v1/volunteers/');
    return response.data;
  }

  async getVolunteer(id: string): Promise<Volunteer> {
    const response = await this.client.get<Volunteer>(`/v1/volunteers/${id}`);
    return response.data;
  }

  async createVolunteer(data: Partial<Volunteer>): Promise<Volunteer> {
    const response = await this.client.post<Volunteer>('/v1/volunteers/', data);
    return response.data;
  }

  async updateVolunteer(id: string, data: Partial<Volunteer>): Promise<Volunteer> {
    const response = await this.client.put<Volunteer>(`/v1/volunteers/${id}`, data);
    return response.data;
  }

  async deleteVolunteer(id: string): Promise<void> {
    await this.client.delete(`/v1/volunteers/${id}`);
  }

  async getEvents(): Promise<Event[]> {
    const response = await this.client.get<Event[]>('/v1/events/');
    return response.data;
  }

  async createEvent(data: Partial<Event>): Promise<Event> {
    const response = await this.client.post<Event>('/v1/events/', data);
    return response.data;
  }
}

export const api = new ApiService();
