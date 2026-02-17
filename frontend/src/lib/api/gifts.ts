import { api, qs } from '$api/client';
import type { Gift } from '$lib/types/models';
import type { PaginatedResponse } from '$lib/types/common';

export interface GiftCreateInput {
  contact_id: string;
  direction: 'given' | 'received' | 'idea';
  name: string;
  description?: string | null;
  amount?: number | null;
  currency?: string;
  status?: string;
  link?: string | null;
}

export type GiftUpdateInput = Partial<GiftCreateInput>;

export const giftsApi = {
  list(vaultId: string, params?: { direction?: string; search?: string; offset?: number; limit?: number }) {
    return api.get<PaginatedResponse<Gift>>(`/vaults/${vaultId}/gifts${qs(params ?? {})}`);
  },

  create(vaultId: string, data: GiftCreateInput) {
    return api.post<Gift>(`/vaults/${vaultId}/gifts`, data);
  },

  del(vaultId: string, giftId: string) {
    return api.del(`/vaults/${vaultId}/gifts/${giftId}`);
  }
};
