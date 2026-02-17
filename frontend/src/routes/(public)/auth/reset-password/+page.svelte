<script lang="ts">
  import { page } from '$app/state';
  import { api } from '$api/client';

  const token = $derived(page.url.searchParams.get('token') ?? '');
  const tokenMissing = $derived(!token);

  let password = $state('');
  let error = $state('');
  let success = $state('');
  let submitting = $state(false);

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    success = '';
    if (!token) {
      error = 'Reset link is missing or invalid.';
      return;
    }
    submitting = true;
    try {
      await api.post('/auth/reset-password', { token, password });
      success = 'Password updated. You can now sign in.';
      password = '';
    } catch (err: any) {
      error = err.detail ?? 'Reset failed';
    } finally {
      submitting = false;
    }
  }
</script>

<form
  onsubmit={handleSubmit}
  class="rounded-xl border border-neutral-800 bg-neutral-900 p-8 shadow-2xl"
>
  <h2 class="mb-2 text-xl font-semibold text-white">Reset password</h2>
  <p class="mb-6 text-sm text-neutral-400">Choose a new password for your account.</p>

  {#if tokenMissing}
    <div class="mb-4 rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">
      Reset link is missing or invalid. Request a new one.
    </div>
  {/if}

  {#if error}
    <div class="mb-4 rounded-lg bg-red-950/50 px-4 py-3 text-sm text-red-400">
      {error}
    </div>
  {/if}

  {#if success}
    <div class="mb-4 rounded-lg bg-emerald-950/50 px-4 py-3 text-sm text-emerald-400">
      {success}
    </div>
  {/if}

  <div class="space-y-4">
    <div>
      <label for="password" class="mb-1.5 block text-sm font-medium text-neutral-300">
        New password
      </label>
      <input
        id="password"
        type="password"
        bind:value={password}
        required
        minlength="8"
        autocomplete="new-password"
        class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
        placeholder="Min 8 characters"
      />
    </div>
  </div>

  <button
    type="submit"
    disabled={submitting || tokenMissing}
    class="mt-6 flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-400 disabled:opacity-50"
  >
    {#if submitting}
      <svg class="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
        <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" class="opacity-75" />
      </svg>
    {/if}
    Reset password
  </button>

  <p class="mt-4 text-center text-sm text-neutral-400">
    Remembered your password?
    <a href="/auth/login" class="text-brand-400 hover:text-brand-300 transition">
      Sign in
    </a>
  </p>
</form>
