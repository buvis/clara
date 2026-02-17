import { api } from '$api/client';
import type { AuthResponse, User } from '$api/types';

export const authApi = {
  login(email: string, password: string): Promise<AuthResponse> {
    return api.post<AuthResponse>('/auth/login', { email, password });
  },

  register(email: string, password: string, name: string): Promise<AuthResponse> {
    return api.post<AuthResponse>('/auth/register', { email, password, name });
  },

  logout(): Promise<void> {
    return api.post('/auth/logout');
  },

  me(): Promise<User> {
    return api.get<User>('/auth/me');
  }
};
