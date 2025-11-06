export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  tenant_id: string;
  role: 'admin' | 'manager' | 'volunteer';
}

export interface Tenant {
  id: string;
  name: string;
  subdomain: string;
  is_active: boolean;
  settings?: Record<string, any>;
}

export interface Volunteer {
  id: string;
  tenant_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  status: 'active' | 'inactive' | 'pending';
  hours_completed: number;
  trainings_completed: string[];
  created_at: string;
}

export interface Event {
  id: string;
  tenant_id: string;
  title: string;
  description?: string;
  event_date: string;
  location?: string;
  max_volunteers?: number;
  registered_volunteers: number;
  created_by: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
