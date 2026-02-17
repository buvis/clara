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
  private contactsLoaded = false;
  private activityTypesLoaded = false;

  async loadContacts(vaultId: string): Promise<void> {
    if (this.contactsLoaded) return;
    try {
      const res = await api.get<PaginatedResponse<Contact>>(
        `/vaults/${vaultId}/contacts?limit=200`
      );
      this.contacts = res.items.map((c) => ({
        id: c.id,
        name: `${c.first_name} ${c.last_name}`.trim()
      }));
      this.contactsLoaded = true;
    } catch {
      this.contacts = [];
    }
  }

  async loadActivityTypes(vaultId: string): Promise<void> {
    if (this.activityTypesLoaded) return;
    try {
      const res = await api.get<PaginatedResponse<ActivityType>>(
        `/vaults/${vaultId}/activity-types?limit=200`
      );
      this.activityTypes = res.items;
      this.activityTypesLoaded = true;
    } catch {
      this.activityTypes = [];
    }
  }

  getContactName(id: string): string {
    return this.contacts.find((c) => c.id === id)?.name ?? 'Unknown';
  }

  invalidate(): void {
    this.contactsLoaded = false;
    this.activityTypesLoaded = false;
    this.contacts = [];
    this.activityTypes = [];
  }
}

export const lookup = new LookupState();
