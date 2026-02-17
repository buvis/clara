<script lang="ts">
  import { page } from '$app/state';
  import { authApi } from '$api/auth';
  import { vaultsApi } from '$api/vaults';
  import { importExportApi } from '$api/importExport';
  import type { TwoFactorSetupResponse } from '$api/types';
  import type { Member } from '$lib/types/models';
  import Button from '$components/ui/Button.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Input from '$components/ui/Input.svelte';

  const vaultId = $derived(page.params.vaultId!);

  const tabs = ['General', 'Members', 'Security', 'Import/Export'] as const;
  type Tab = (typeof tabs)[number];
  let activeTab = $state<Tab>('General');

  let settingsLoading = $state(true);
  let settingsSaving = $state(false);
  let settingsMessage = $state('');
  let settingsError = $state('');
  let settingsForm = $state({
    language: 'en',
    date_format: 'YYYY-MM-DD',
    time_format: '24h',
    timezone: 'UTC',
    debts: true,
    gifts: true,
    pets: true,
    journal: true
  });

  let members = $state<Member[]>([]);
  let membersLoading = $state(true);
  let inviteEmail = $state('');
  let inviteRole = $state('member');
  let inviting = $state(false);

  let importLoading = $state(false);
  let importMessage = $state('');
  let importError = $state('');

  let setup = $state<TwoFactorSetupResponse | null>(null);
  let setupLoading = $state(false);
  let setupError = $state('');
  let confirmCode = $state('');
  let confirmLoading = $state(false);
  let confirmError = $state('');
  let confirmSuccess = $state(false);
  let disableLoading = $state(false);
  let disableMessage = $state('');
  let disableError = $state('');

  function parseFeatureFlags(raw: string): { debts: boolean; gifts: boolean; pets: boolean; journal: boolean } {
    try {
      const parsed = JSON.parse(raw || '{}');
      return {
        debts: parsed.debts !== false,
        gifts: parsed.gifts !== false,
        pets: parsed.pets !== false,
        journal: parsed.journal !== false
      };
    } catch {
      return { debts: true, gifts: true, pets: true, journal: true };
    }
  }

  function toFeatureFlags() {
    return JSON.stringify({
      debts: settingsForm.debts,
      gifts: settingsForm.gifts,
      pets: settingsForm.pets,
      journal: settingsForm.journal
    });
  }

  async function loadSettings() {
    settingsLoading = true;
    settingsError = '';
    try {
      const settings = await vaultsApi.getSettings(vaultId);
      const flags = parseFeatureFlags(settings.feature_flags);
      settingsForm = {
        language: settings.language,
        date_format: settings.date_format,
        time_format: settings.time_format,
        timezone: settings.timezone,
        debts: flags.debts,
        gifts: flags.gifts,
        pets: flags.pets,
        journal: flags.journal
      };
    } catch (err: any) {
      settingsError = err.detail ?? 'Failed to load settings';
    } finally {
      settingsLoading = false;
    }
  }

  async function saveSettings() {
    settingsSaving = true;
    settingsMessage = '';
    settingsError = '';
    try {
      await vaultsApi.updateSettings(vaultId, {
        language: settingsForm.language,
        date_format: settingsForm.date_format,
        time_format: settingsForm.time_format,
        timezone: settingsForm.timezone,
        feature_flags: toFeatureFlags()
      });
      settingsMessage = 'Settings saved.';
    } catch (err: any) {
      settingsError = err.detail ?? 'Failed to save settings';
    } finally {
      settingsSaving = false;
    }
  }

  async function loadMembers() {
    membersLoading = true;
    try {
      members = await vaultsApi.listMembers(vaultId);
    } finally {
      membersLoading = false;
    }
  }

  async function handleInvite() {
    if (!inviteEmail.trim()) return;
    inviting = true;
    try {
      await vaultsApi.inviteMember(vaultId, { email: inviteEmail, role: inviteRole });
      inviteEmail = '';
      inviteRole = 'member';
      await loadMembers();
    } finally {
      inviting = false;
    }
  }

  async function handleRoleChange(member: Member, role: string) {
    await vaultsApi.updateMemberRole(vaultId, member.user_id, role);
    await loadMembers();
  }

  async function handleRemove(member: Member) {
    await vaultsApi.removeMember(vaultId, member.user_id);
    await loadMembers();
  }

  async function handleImportVcard(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    importLoading = true;
    importMessage = '';
    importError = '';
    try {
      await importExportApi.importVcard(vaultId, file);
      importMessage = 'vCard import completed.';
    } catch (err: any) {
      importError = err.message ?? 'Import failed';
    } finally {
      importLoading = false;
      input.value = '';
    }
  }

  async function handleImportCsv(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    importLoading = true;
    importMessage = '';
    importError = '';
    try {
      await importExportApi.importCsv(vaultId, file);
      importMessage = 'CSV import completed.';
    } catch (err: any) {
      importError = err.message ?? 'Import failed';
    } finally {
      importLoading = false;
      input.value = '';
    }
  }

  async function handleSetup() {
    setupError = '';
    disableMessage = '';
    disableError = '';
    setupLoading = true;
    try {
      setup = await authApi.setupTwoFactor();
      confirmSuccess = false;
      confirmCode = '';
    } catch (err: any) {
      setupError = err.detail ?? 'Failed to start 2FA setup';
    } finally {
      setupLoading = false;
    }
  }

  async function handleConfirm(e: SubmitEvent) {
    e.preventDefault();
    confirmError = '';
    confirmLoading = true;
    try {
      await authApi.confirmTwoFactor({ code: confirmCode });
      confirmSuccess = true;
    } catch (err: any) {
      confirmError = err.detail ?? 'Invalid verification code';
    } finally {
      confirmLoading = false;
    }
  }

  async function handleDisable() {
    disableError = '';
    disableMessage = '';
    disableLoading = true;
    try {
      await authApi.disableTwoFactor();
      setup = null;
      confirmSuccess = false;
      confirmCode = '';
      disableMessage = 'Two-factor authentication disabled.';
    } catch (err: any) {
      disableError = err.detail ?? 'Failed to disable two-factor authentication';
    } finally {
      disableLoading = false;
    }
  }

  $effect(() => {
    if (!vaultId) return;
    loadSettings();
    loadMembers();
  });
</script>

<svelte:head>
  <title>Settings</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-semibold text-white">Settings</h1>
    <p class="text-sm text-neutral-400">Manage vault preferences for {vaultId}.</p>
  </div>

  <div class="flex flex-wrap gap-2">
    {#each tabs as tab}
      <button
        type="button"
        class="rounded-lg px-3 py-1.5 text-sm transition {activeTab === tab
          ? 'bg-brand-500/10 text-brand-400'
          : 'text-neutral-400 hover:bg-neutral-800 hover:text-white'}"
        onclick={() => (activeTab = tab)}
      >
        {tab}
      </button>
    {/each}
  </div>

  {#if activeTab === 'General'}
    <section class="space-y-4 rounded-xl border border-neutral-800 bg-neutral-900 p-6">
      {#if settingsError}
        <div class="rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">{settingsError}</div>
      {/if}
      {#if settingsMessage}
        <div class="rounded-lg bg-emerald-950/50 px-4 py-3 text-sm text-emerald-300">{settingsMessage}</div>
      {/if}

      {#if settingsLoading}
        <p class="text-sm text-neutral-500">Loading settings…</p>
      {:else}
        <div class="grid gap-4 md:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-neutral-300">Language</label>
            <select
              bind:value={settingsForm.language}
              class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-neutral-300">Date format</label>
            <select
              bind:value={settingsForm.date_format}
              class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500"
            >
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-neutral-300">Time format</label>
            <select
              bind:value={settingsForm.time_format}
              class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500"
            >
              <option value="24h">24-hour</option>
              <option value="12h">12-hour</option>
            </select>
          </div>
          <Input label="Timezone" bind:value={settingsForm.timezone} />
        </div>

        <div>
          <h3 class="text-sm font-medium text-neutral-300">Feature flags</h3>
          <div class="mt-3 grid gap-3 sm:grid-cols-2">
            <label class="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-300">
              Debts
              <input type="checkbox" bind:checked={settingsForm.debts} class="h-4 w-4 accent-brand-500" />
            </label>
            <label class="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-300">
              Gifts
              <input type="checkbox" bind:checked={settingsForm.gifts} class="h-4 w-4 accent-brand-500" />
            </label>
            <label class="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-300">
              Pets
              <input type="checkbox" bind:checked={settingsForm.pets} class="h-4 w-4 accent-brand-500" />
            </label>
            <label class="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-300">
              Journal
              <input type="checkbox" bind:checked={settingsForm.journal} class="h-4 w-4 accent-brand-500" />
            </label>
          </div>
        </div>

        <div class="flex justify-end">
          <Button onclick={saveSettings} loading={settingsSaving}>Save settings</Button>
        </div>
      {/if}
    </section>
  {/if}

  {#if activeTab === 'Members'}
    <section class="space-y-4 rounded-xl border border-neutral-800 bg-neutral-900 p-6">
      <div class="space-y-2">
        <h2 class="text-lg font-semibold text-white">Members</h2>
        {#if membersLoading}
          <p class="text-sm text-neutral-500">Loading members…</p>
        {:else if members.length === 0}
          <p class="text-sm text-neutral-500">No members yet.</p>
        {:else}
          <div class="space-y-2">
            {#each members as member}
              <div class="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2">
                <div>
                  <p class="text-sm font-medium text-white">{member.name || member.email}</p>
                  <p class="text-xs text-neutral-500">{member.email}</p>
                </div>
                <div class="flex items-center gap-2">
                  <Badge text={member.role} variant={member.role === 'owner' ? 'warning' : 'default'} />
                  <select
                    value={member.role}
                    onchange={(e) => handleRoleChange(member, (e.target as HTMLSelectElement).value)}
                    class="rounded-lg border border-neutral-700 bg-neutral-800 px-2 py-1 text-xs text-white outline-none transition focus:border-brand-500"
                  >
                    <option value="owner">Owner</option>
                    <option value="admin">Admin</option>
                    <option value="member">Member</option>
                    <option value="viewer">Viewer</option>
                  </select>
                  <Button size="sm" variant="ghost" onclick={() => handleRemove(member)}>Remove</Button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <form onsubmit={handleInvite} class="grid gap-3 rounded-lg border border-neutral-800 bg-neutral-950 p-4 md:grid-cols-[1fr_auto_auto] md:items-end">
        <Input label="Invite email" type="email" bind:value={inviteEmail} required />
        <div>
          <label class="mb-1.5 block text-sm font-medium text-neutral-300">Role</label>
          <select
            bind:value={inviteRole}
            class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500"
          >
            <option value="member">Member</option>
            <option value="admin">Admin</option>
            <option value="viewer">Viewer</option>
          </select>
        </div>
        <Button type="submit" loading={inviting}>Invite</Button>
      </form>
    </section>
  {/if}

  {#if activeTab === 'Security'}
    <section class="rounded-xl border border-neutral-800 bg-neutral-900 p-6">
      <div class="flex flex-col gap-1">
        <h2 class="text-lg font-semibold text-white">Two-Factor Authentication</h2>
        <p class="text-sm text-neutral-400">
          Add an extra layer of protection with an authenticator app and recovery codes.
        </p>
      </div>

      {#if setupError}
        <div class="mt-4 rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">
          {setupError}
        </div>
      {/if}

      {#if disableMessage}
        <div class="mt-4 rounded-lg bg-emerald-950/50 px-4 py-3 text-sm text-emerald-300">
          {disableMessage}
        </div>
      {/if}

      {#if disableError}
        <div class="mt-4 rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">
          {disableError}
        </div>
      {/if}

      <div class="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          disabled={setupLoading}
          class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-400 disabled:opacity-50"
          onclick={handleSetup}
        >
          {setupLoading ? 'Starting setup…' : 'Enable 2FA'}
        </button>
        <button
          type="button"
          disabled={disableLoading}
          class="rounded-lg border border-neutral-700 px-4 py-2 text-sm font-medium text-neutral-200 transition hover:border-neutral-500 disabled:opacity-50"
          onclick={handleDisable}
        >
          {disableLoading ? 'Disabling…' : 'Disable 2FA'}
        </button>
      </div>

      {#if setup}
        <div class="mt-6 grid gap-6 lg:grid-cols-[220px_1fr]">
          <div class="rounded-lg border border-neutral-800 bg-neutral-950 p-4">
            <p class="text-xs uppercase tracking-wide text-neutral-500">Scan QR Code</p>
            <img
              class="mt-3 w-full rounded-md border border-neutral-800 bg-white p-2"
              src={setup.qr_data_url}
              alt="CLARA 2FA QR code"
            />
            <p class="mt-3 text-xs text-neutral-500">Or enter this key:</p>
            <p class="mt-1 break-all text-xs text-neutral-200">{setup.provisioning_uri}</p>
          </div>

          <div class="space-y-4">
            <div class="rounded-lg border border-neutral-800 bg-neutral-950 p-4">
              <p class="text-xs uppercase tracking-wide text-neutral-500">Recovery Codes</p>
              <p class="mt-2 text-sm text-neutral-400">
                Save these codes somewhere safe. Each code can be used once.
              </p>
              <div class="mt-3 grid gap-2 sm:grid-cols-2">
                {#each setup.recovery_codes as code}
                  <div class="rounded-md border border-neutral-800 bg-neutral-900 px-3 py-2 text-sm font-mono text-neutral-200">
                    {code}
                  </div>
                {/each}
              </div>
            </div>

            <form onsubmit={handleConfirm} class="rounded-lg border border-neutral-800 bg-neutral-950 p-4">
              <p class="text-xs uppercase tracking-wide text-neutral-500">Verify Setup</p>

              {#if confirmError}
                <div class="mt-3 rounded-lg bg-red-950/50 px-3 py-2 text-sm text-red-400">
                  {confirmError}
                </div>
              {/if}

              {#if confirmSuccess}
                <div class="mt-3 rounded-lg bg-emerald-950/50 px-3 py-2 text-sm text-emerald-300">
                  Two-factor authentication enabled.
                </div>
              {/if}

              <div class="mt-3">
                <label for="confirm-code" class="mb-1.5 block text-sm font-medium text-neutral-300">
                  Authenticator code
                </label>
                <input
                  id="confirm-code"
                  type="text"
                  bind:value={confirmCode}
                  required
                  autocomplete="one-time-code"
                  class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                  placeholder="123456"
                />
              </div>

              <button
                type="submit"
                disabled={confirmLoading}
                class="mt-4 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-400 disabled:opacity-50"
              >
                {confirmLoading ? 'Verifying…' : 'Confirm 2FA'}
              </button>
            </form>
          </div>
        </div>
      {/if}
    </section>
  {/if}

  {#if activeTab === 'Import/Export'}
    <section class="space-y-4 rounded-xl border border-neutral-800 bg-neutral-900 p-6">
      <input id="import-vcard" type="file" accept=".vcf,text/vcard" class="hidden" onchange={handleImportVcard} />
      <input id="import-csv" type="file" accept=".csv,text/csv" class="hidden" onchange={handleImportCsv} />

      {#if importMessage}
        <div class="rounded-lg bg-emerald-950/50 px-4 py-3 text-sm text-emerald-300">{importMessage}</div>
      {/if}
      {#if importError}
        <div class="rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">{importError}</div>
      {/if}

      <div class="space-y-2">
        <h2 class="text-lg font-semibold text-white">Import</h2>
        <div class="flex flex-wrap gap-3">
          <Button loading={importLoading} onclick={() => document.getElementById('import-vcard')?.click()}>
            Import vCard
          </Button>
          <Button loading={importLoading} variant="secondary" onclick={() => document.getElementById('import-csv')?.click()}>
            Import CSV
          </Button>
        </div>
      </div>

      <div class="space-y-2">
        <h2 class="text-lg font-semibold text-white">Export</h2>
        <div class="flex flex-wrap gap-3">
          <Button variant="secondary" onclick={() => importExportApi.exportVcard(vaultId)}>Export vCard</Button>
          <Button variant="secondary" onclick={() => importExportApi.exportCsv(vaultId)}>Export CSV</Button>
          <Button variant="secondary" onclick={() => importExportApi.exportJson(vaultId)}>Export JSON</Button>
        </div>
      </div>
    </section>
  {/if}
</div>
