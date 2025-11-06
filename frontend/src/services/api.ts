// frontend/src/services/api.ts
import axios, { AxiosInstance } from 'axios';
import { LoginRequest, TokenResponse, User, Volunteer, Event } from '../types';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    // Use the correct API URL
    const baseURL = process.env.NODE_ENV === 'development' 
		? 'http://localhost:8000/api'
		: 'https://api.vvhs-saas.sitevision.com/api';
      
    this.client = axios.create({
      baseURL: baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: false,
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
	const response = await this.client.post<TokenResponse>('/v1/auth/login', data); // Send as JSON
	this.setToken(response.data.access_token);
	// Store refresh token too
	localStorage.setItem('refresh_token', response.data.refresh_token);
	return response.data;
  }
  
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/v1/users/me');
    return response.data;
  }

  async logout() {
    await this.client.post('/v1/auth/logout');
    this.clearToken();
  }

  async getVolunteers(): Promise<Volunteer[]> {
    const response = await this.client.get<{total: number, items: Volunteer[]}>('/v1/volunteers/');
    return response.data.items; 
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
