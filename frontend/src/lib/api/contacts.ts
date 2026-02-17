import { api, qs } from '$api/client';
import type { Contact } from '$lib/types/models';
import type { PaginatedResponse } from '$lib/types/common';

export interface ContactCreateInput {
  first_name: string;
  last_name?: string;
  nickname?: string | null;
  birthdate?: string | null;
  gender?: string | null;
  pronouns?: string | null;
  notes_summary?: string | null;
  favorite?: boolean;
}

export type ContactUpdateInput = Partial<ContactCreateInput>;

export const contactsApi = {
  list(vaultId: string, params?: { q?: string; favorites?: boolean; offset?: number; limit?: number }) {
    return api.get<PaginatedResponse<Contact>>(`/vaults/${vaultId}/contacts${qs(params ?? {})}`);
  },

  get(vaultId: string, contactId: string) {
    return api.get<Contact>(`/vaults/${vaultId}/contacts/${contactId}`);
  },

  create(vaultId: string, data: ContactCreateInput) {
    return api.post<Contact>(`/vaults/${vaultId}/contacts`, data);
  },

  update(vaultId: string, contactId: string, data: ContactUpdateInput) {
    return api.patch<Contact>(`/vaults/${vaultId}/contacts/${contactId}`, data);
  },

  del(vaultId: string, contactId: string) {
    return api.del(`/vaults/${vaultId}/contacts/${contactId}`);
  }
};
