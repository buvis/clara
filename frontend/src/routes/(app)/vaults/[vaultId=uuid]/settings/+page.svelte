<script lang="ts">
  import { page } from '$app/state';
  import { authApi } from '$api/auth';
  import type { TwoFactorSetupResponse } from '$api/types';

  const vaultId = $derived(page.params.vaultId!);

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
</script>

<svelte:head>
  <title>Settings</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-semibold text-white">Settings</h1>
    <p class="text-sm text-neutral-400">Manage vault preferences for {vaultId}.</p>
  </div>

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
</div>
