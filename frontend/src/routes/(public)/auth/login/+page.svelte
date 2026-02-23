<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$state/auth.svelte';

  let email = $state('');
  let password = $state('');
  let error = $state('');
  let submitting = $state(false);
  let tempToken = $state('');
  let twoFactorCode = $state('');
  let twoFactorMode = $state<'totp' | 'recovery' | null>(null);
  let twoFactorError = $state('');
  let verifying = $state(false);

  function handleAuthRedirect(vaultId: string | null) {
    const saved = sessionStorage.getItem('clara_redirect');
    sessionStorage.removeItem('clara_redirect');
    if (saved && saved.startsWith('/')) {
      goto(saved);
    } else if (vaultId) {
      goto(`/vaults/${vaultId}/dashboard`);
    } else {
      goto('/');
    }
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    submitting = true;
    try {
      const res = await auth.login(email, password);
      if ('requires_2fa' in res) {
        tempToken = res.temp_token;
        twoFactorMode = 'totp';
        twoFactorCode = '';
        password = '';
        return;
      }
      handleAuthRedirect(res.vault_id);
    } catch (err: any) {
      error = err.detail ?? 'Login failed';
    } finally {
      submitting = false;
    }
  }

  async function handleTwoFactorSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!tempToken) {
      twoFactorError = 'Missing 2FA token. Please sign in again.';
      return;
    }
    twoFactorError = '';
    verifying = true;
    try {
      const res = await auth.verifyTwoFactor(
        tempToken,
        twoFactorCode,
        twoFactorMode === 'recovery'
      );
      handleAuthRedirect(res.vault_id);
    } catch (err: any) {
      twoFactorError = err.detail ?? 'Verification failed';
    } finally {
      verifying = false;
    }
  }
</script>

{#if twoFactorMode}
  <form
    onsubmit={handleTwoFactorSubmit}
    class="rounded-xl border border-neutral-800 bg-neutral-900 p-8 shadow-2xl"
  >
    <h2 class="mb-6 text-xl font-semibold text-white">Two-factor verification</h2>

    {#if twoFactorError}
      <div class="mb-4 rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">
        {twoFactorError}
      </div>
    {/if}

    <div>
      <label for="two-factor-code" class="mb-1.5 block text-sm font-medium text-neutral-300">
        {twoFactorMode === 'recovery' ? 'Recovery code' : 'Authenticator code'}
      </label>
      <input
        id="two-factor-code"
        type="text"
        bind:value={twoFactorCode}
        required
        autocomplete="one-time-code"
        class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
        placeholder={twoFactorMode === 'recovery' ? '8-character code' : '123456'}
      />
    </div>

    <button
      type="submit"
      disabled={verifying}
      class="mt-6 flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-400 disabled:opacity-50"
    >
      {#if verifying}
        <svg class="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
          <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" class="opacity-75" />
        </svg>
      {/if}
      Verify
    </button>

    <div class="mt-4 flex items-center justify-between text-sm text-neutral-400">
      <button
        type="button"
        class="text-brand-400 hover:text-brand-300 transition"
        onclick={() => (twoFactorMode = twoFactorMode === 'recovery' ? 'totp' : 'recovery')}
      >
        {twoFactorMode === 'recovery' ? 'Use authenticator code' : 'Use recovery code'}
      </button>
      <button
        type="button"
        class="text-neutral-400 hover:text-neutral-200 transition"
        onclick={() => {
          twoFactorMode = null;
          tempToken = '';
          twoFactorCode = '';
          twoFactorError = '';
        }}
      >
        Back to sign in
      </button>
    </div>
  </form>
{:else}
  <form
    onsubmit={handleSubmit}
    class="rounded-xl border border-neutral-800 bg-neutral-900 p-8 shadow-2xl"
  >
    <h2 class="mb-6 text-xl font-semibold text-white">Sign in</h2>

    {#if error}
      <div class="mb-4 rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">
        {error}
      </div>
    {/if}

    <div class="space-y-4">
      <div>
        <label for="email" class="mb-1.5 block text-sm font-medium text-neutral-300">
          Email
        </label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          autocomplete="email"
          class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          placeholder="you@example.com"
        />
      </div>

      <div>
        <label for="password" class="mb-1.5 block text-sm font-medium text-neutral-300">
          Password
        </label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          autocomplete="current-password"
          class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          placeholder="********"
        />
      </div>
    </div>

    <button
      type="submit"
      disabled={submitting}
      class="mt-6 flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-400 disabled:opacity-50"
    >
      {#if submitting}
        <svg class="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
          <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" class="opacity-75" />
        </svg>
      {/if}
      Sign in
    </button>

    <p class="mt-4 text-center text-sm text-neutral-400">
      No account?
      <a href="/auth/register" class="text-brand-400 hover:text-brand-300 transition">
        Create one
      </a>
    </p>
  </form>
{/if}
