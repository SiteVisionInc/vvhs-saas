// frontend/src/types/index.ts
export interface User {
  id: number | string;
  username?: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  tenant_id: number | string;
  role: 'system_admin' | 'org_admin' | 'coordinator' | 'sub_unit_staff' | 'volunteer' | 'admin' | 'manager';
  status?: 'active' | 'inactive' | 'suspended' | 'pending';
  // Permission fields
  can_view_data?: boolean;
  can_edit_data?: boolean;
  can_export_data?: boolean;
  mfa_enabled?: boolean;
  created_at?: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug?: string;
  subdomain?: string;
  contact_email?: string;
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
  status: 'approved' | 'pending' | 'incomplete' | 'working' | 'rejected' | 'inactive' | 'active';
  hours_completed?: number;
  total_hours?: number;
  trainings_completed?: string[];
  application_status?: string;
  account_status?: string;
  created_at: string;
}

export interface Event {
  id: string;
  tenant_id: string;
  title: string;
  name?: string;
  description?: string;
  event_date?: string;
  start_date?: string;
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
  refresh_token: string;  
  token_type: string;
}

// Additional types for API responses
export interface VolunteerListResponse {
  total: number;
  items: Volunteer[];
}

export interface UserListResponse {
  total: number;
  items: User[];
}

export interface EventListResponse {
  total: number;
  items: Event[];
}