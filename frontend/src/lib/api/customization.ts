import { api, qs } from '$api/client';
import type { Template, CustomField } from '$lib/types/models';
import type { PaginatedResponse } from '$lib/types/common';

export interface TemplateCreateInput {
  name: string;
  pages?: string;
  modules?: string;
}

export type TemplateUpdateInput = Partial<TemplateCreateInput>;

export interface CustomFieldCreateInput {
  scope: string;
  name: string;
  slug: string;
  data_type: string;
  config_json?: string | null;
}

export const customizationApi = {
  listTemplates(vaultId: string, params?: { offset?: number; limit?: number }) {
    return api.get<PaginatedResponse<Template>>(`/vaults/${vaultId}/templates${qs(params ?? {})}`);
  },

  getTemplate(vaultId: string, templateId: string) {
    return api.get<Template>(`/vaults/${vaultId}/templates/${templateId}`);
  },

  createTemplate(vaultId: string, data: TemplateCreateInput) {
    return api.post<Template>(`/vaults/${vaultId}/templates`, data);
  },

  updateTemplate(vaultId: string, templateId: string, data: TemplateUpdateInput) {
    return api.patch<Template>(`/vaults/${vaultId}/templates/${templateId}`, data);
  },

  deleteTemplate(vaultId: string, templateId: string) {
    return api.del(`/vaults/${vaultId}/templates/${templateId}`);
  },

  listCustomFields(vaultId: string, params?: { offset?: number; limit?: number; scope?: string }) {
    return api.get<PaginatedResponse<CustomField>>(`/vaults/${vaultId}/custom-fields/definitions${qs(params ?? {})}`);
  },

  createCustomField(vaultId: string, data: CustomFieldCreateInput) {
    return api.post<CustomField>(`/vaults/${vaultId}/custom-fields/definitions`, data);
  },

  updateCustomField(vaultId: string, fieldId: string, data: Partial<CustomFieldCreateInput>) {
    return api.patch<CustomField>(`/vaults/${vaultId}/custom-fields/definitions/${fieldId}`, data);
  },

  deleteCustomField(vaultId: string, fieldId: string) {
    return api.del(`/vaults/${vaultId}/custom-fields/definitions/${fieldId}`);
  }
};
