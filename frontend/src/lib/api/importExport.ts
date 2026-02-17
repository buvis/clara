import { api } from '$api/client';

export const importExportApi = {
  async importVcard(vaultId: string, file: File) {
    const form = new FormData();
    form.append('file', file);
    const csrf = document.cookie
      .split('; ')
      .find((c) => c.startsWith('csrf_token='))
      ?.split('=')[1];
    const headers: Record<string, string> = {};
    if (csrf) headers['x-csrf-token'] = csrf;
    const res = await fetch(`/api/v1/vaults/${vaultId}/import/vcard`, {
      method: 'POST',
      credentials: 'include',
      headers,
      body: form
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail ?? 'Import failed');
    }
    return await res.json();
  },

  async importCsv(vaultId: string, file: File) {
    const form = new FormData();
    form.append('file', file);
    const csrf = document.cookie
      .split('; ')
      .find((c) => c.startsWith('csrf_token='))
      ?.split('=')[1];
    const headers: Record<string, string> = {};
    if (csrf) headers['x-csrf-token'] = csrf;
    const res = await fetch(`/api/v1/vaults/${vaultId}/import/csv`, {
      method: 'POST',
      credentials: 'include',
      headers,
      body: form
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail ?? 'Import failed');
    }
    return await res.json();
  },

  exportVcard(vaultId: string) {
    window.open(`/api/v1/vaults/${vaultId}/export/vcard`, '_blank');
  },

  exportCsv(vaultId: string) {
    window.open(`/api/v1/vaults/${vaultId}/export/csv`, '_blank');
  },

  exportJson(vaultId: string) {
    window.open(`/api/v1/vaults/${vaultId}/export/json`, '_blank');
  }
};
