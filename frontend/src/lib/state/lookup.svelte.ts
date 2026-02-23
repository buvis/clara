import { api } from '$api/client';
import type { Contact, ActivityType } from '$api/types';
import type { PaginatedResponse } from '$lib/types/common';

interface ContactLookup {
  id: string;
  name: string;
}

class LookupState {
  contacts = $state<ContactLookup[]>([]);
  activityTypes = $state<ActivityType[]>([]);
  private contactsVaultId: string | null = null;
  private activityTypesVaultId: string | null = null;

  async loadContacts(vaultId: string): Promise<void> {
    if (this.contactsVaultId === vaultId) return;
    try {
      const res = await api.get<PaginatedResponse<Contact>>(
        `/vaults/${vaultId}/contacts?limit=1000`
      );
      this.contacts = res.items.map((c) => ({
        id: c.id,
        name: `${c.first_name} ${c.last_name}`.trim()
      }));
      this.contactsVaultId = vaultId;
    } catch {
      this.contacts = [];
    }
  }

  async loadActivityTypes(vaultId: string): Promise<void> {
    if (this.activityTypesVaultId === vaultId) return;
    try {
      const res = await api.get<PaginatedResponse<ActivityType>>(
        `/vaults/${vaultId}/activities/types?limit=1000`
      );
      this.activityTypes = res.items;
      this.activityTypesVaultId = vaultId;
    } catch {
      this.activityTypes = [];
    }
  }

  getContactName(id: string): string {
    return this.contacts.find((c) => c.id === id)?.name ?? 'Unknown';
  }

  invalidate(): void {
    this.contactsVaultId = null;
    this.activityTypesVaultId = null;
    this.contacts = [];
    this.activityTypes = [];
  }
}

export const lookup = new LookupState();
