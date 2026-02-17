import { api } from '$api/client';
import type { Vault } from '$api/types';

class VaultState {
  vaults = $state<Vault[]>([]);
  current = $state<Vault | null>(null);
  loading = $state(false);

  get currentId(): string | null {
    return this.current?.id ?? null;
  }

  async fetchVaults(): Promise<void> {
    this.loading = true;
    try {
      this.vaults = await api.get<Vault[]>('/vaults');
    } catch {
      this.vaults = [];
    } finally {
      this.loading = false;
    }
  }

  async fetchVault(id: string): Promise<Vault> {
    const vault = await api.get<Vault>(`/vaults/${id}`);
    this.current = vault;
    return vault;
  }

  setCurrent(vault: Vault): void {
    this.current = vault;
  }

  async createVault(name: string): Promise<Vault> {
    const vault = await api.post<Vault>('/vaults', { name });
    this.vaults = [...this.vaults, vault];
    return vault;
  }
}

export const vaultState = new VaultState();
