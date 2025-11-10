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
  
  // ----- Scheduling -----
  async getAvailableShifts(startDate?: string, endDate?: string, includeFull?: boolean) {
	const params = new URLSearchParams();
	if (startDate) params.append('start_date', startDate);
	if (endDate) params.append('end_date', endDate);
	if (includeFull) params.append('include_full', 'true');
	
	const res = await this.client.get(`/v1/scheduling/shifts/available?${params}`);
	return res.data;
  }
	
  async signupForShift(shiftId: number, notes?: string) {
	const res = await this.client.post(`/v1/scheduling/shifts/${shiftId}/signup`, {
	 shift_id: shiftId,
	 notes: notes || ''
	});
	return res.data;
  }
	
  async joinWaitlist(shiftId: number, autoAccept: boolean = true) {
	const res = await this.client.post(`/v1/scheduling/shifts/${shiftId}/waitlist`, {
	 shift_id: shiftId,
	 auto_accept: autoAccept
	});
	return res.data;
  }
	
  async getMyWaitlists() {
	const res = await this.client.get('/v1/scheduling/waitlists/mine');
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
  
  async getVolunteerStats(): Promise<{
	total_volunteers: number;
	approved_volunteers: number;
	pending_applications: number;
	incomplete_applications: number;
	working_volunteers: number;
	}> {
	const response = await this.client.get('/v1/volunteers/stats');
	return response.data;
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
  
  
    // ============================================================================
  // BEHAVIORAL HEALTH MODULE API METHODS
  // ============================================================================

  // ----- BH Patients -----
  async getBHPatients(params?: { skip?: number; limit?: number; risk_level?: string }) {
    const res = await this.client.get('/v1/bh/patients', { params });
    return res.data;
  }

  async getBHPatient(patientId: number) {
    const res = await this.client.get(`/v1/bh/patients/${patientId}`);
    return res.data;
  }

  async createBHPatient(data: any) {
    const res = await this.client.post('/v1/bh/patients', data);
    return res.data;
  }

  async updateBHPatient(patientId: number, data: any) {
    const res = await this.client.put(`/v1/bh/patients/${patientId}`, data);
    return res.data;
  }

  // ----- BH Screenings -----
  async createBHScreening(data: any) {
    const res = await this.client.post('/v1/bh/patients/screenings', data);
    return res.data;
  }

  async getBHPatientScreenings(patientId: number) {
    const res = await this.client.get(`/v1/bh/patients/${patientId}/screenings`);
    return res.data;
  }

  // ----- BH Consent -----
  async captureBHConsent(patientId: number, data: any) {
    const res = await this.client.post(`/v1/bh/patients/${patientId}/consent`, data);
    return res.data;
  }

  async getBHPatientConsents(patientId: number) {
    const res = await this.client.get(`/v1/bh/patients/${patientId}/consents`);
    return res.data;
  }

  // ----- BH Facilities -----
  async getBHFacilities(params?: { 
    skip?: number; 
    limit?: number; 
    facility_type?: string; 
    is_active?: boolean 
  }) {
    const res = await this.client.get('/v1/bh/facilities', { params });
    return res.data;
  }

  async getBHFacility(facilityId: number) {
    const res = await this.client.get(`/v1/bh/facilities/${facilityId}`);
    return res.data;
  }

  async createBHFacility(data: any) {
    const res = await this.client.post('/v1/bh/facilities', data);
    return res.data;
  }

  async updateBHFacility(facilityId: number, data: any) {
    const res = await this.client.put(`/v1/bh/facilities/${facilityId}`, data);
    return res.data;
  }

  // ----- BH Bed Availability -----
  async updateBHBedAvailability(data: any) {
    const res = await this.client.post('/v1/bh/facilities/beds/update', data);
    return res.data;
  }

  async getBHFacilityBeds(facilityId: number) {
    const res = await this.client.get(`/v1/bh/facilities/${facilityId}/beds`);
    return res.data;
  }

  async searchBHBeds(searchParams: any) {
    const res = await this.client.post('/v1/bh/facilities/search', searchParams);
    return res.data;
  }

  async getBHStaleBedAlerts(hoursThreshold: number = 24) {
    const res = await this.client.get('/v1/bh/facilities/beds/stale-alerts', {
      params: { hours_threshold: hoursThreshold }
    });
    return res.data;
  }

  // ----- BH Referrals -----
  async getBHReferrals(params?: { 
    skip?: number; 
    limit?: number; 
    status?: string; 
    priority?: string 
  }) {
    const res = await this.client.get('/v1/bh/referrals', { params });
    return res.data;
  }

  async getBHReferral(referralId: number) {
    const res = await this.client.get(`/v1/bh/referrals/${referralId}`);
    return res.data;
  }

  async createBHReferral(data: any) {
    const res = await this.client.post('/v1/bh/referrals', data);
    return res.data;
  }

  async updateBHReferral(referralId: number, data: any) {
    const res = await this.client.put(`/v1/bh/referrals/${referralId}`, data);
    return res.data;
  }

  async submitBHReferral(referralId: number, facilityIds: number[]) {
    const res = await this.client.post(`/v1/bh/referrals/${referralId}/submit`, { facility_ids: facilityIds });
    return res.data;
  }

  async acceptBHReferral(referralId: number, data: any) {
    const res = await this.client.post(`/v1/bh/referrals/${referralId}/accept`, data);
    return res.data;
  }

  async declineBHReferral(referralId: number, data: any) {
    const res = await this.client.post(`/v1/bh/referrals/${referralId}/decline`, data);
    return res.data;
  }

  // ----- BH Placements -----
  async dischargeBHPlacement(placementId: number, data: any) {
    const res = await this.client.patch(`/v1/bh/referrals/placements/${placementId}/discharge`, data);
    return res.data;
  }

  // ----- BH Follow-ups -----
  async createBHFollowup(placementId: number, data: any) {
    const res = await this.client.post(`/v1/bh/referrals/placements/${placementId}/followups`, data);
    return res.data;
  }

  async completeBHFollowup(followupId: number, data: any) {
    const res = await this.client.patch(`/v1/bh/referrals/followups/${followupId}/complete`, data);
    return res.data;
  }

  async getBHDueFollowups(daysAhead: number = 7) {
    const res = await this.client.get('/v1/bh/referrals/followups/due', {
      params: { days_ahead: daysAhead }
    });
    return res.data;
  }

  // ----- BH Statistics -----
  async getBHStatistics() {
    try {
      const [patients, referrals, facilities, beds] = await Promise.all([
        this.getBHPatients({ limit: 1000 }),
        this.getBHReferrals({ limit: 1000 }),
        this.getBHFacilities({ is_active: true }),
        this.searchBHBeds({ min_available: 1 })
      ]);

      return {
        total_patients: patients.length || 0,
        total_referrals: referrals.length || 0,
        pending_referrals: referrals.filter((r: any) => r.status === 'submitted').length || 0,
        active_placements: referrals.filter((r: any) => r.status === 'placed').length || 0,
        available_beds: beds.reduce((sum: number, b: any) => sum + (b.available_beds || 0), 0),
        total_facilities: facilities.length || 0
      };
    } catch (error) {
      console.error('Failed to load BH statistics:', error);
      return {
        total_patients: 0,
        total_referrals: 0,
        pending_referrals: 0,
        active_placements: 0,
        available_beds: 0,
        total_facilities: 0
      };
    }
  }
  
}

export const api = new ApiService();
