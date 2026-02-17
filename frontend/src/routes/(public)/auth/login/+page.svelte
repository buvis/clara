<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$state/auth.svelte';

  let email = $state('');
  let password = $state('');
  let error = $state('');
  let submitting = $state(false);

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    submitting = true;
    try {
      const res = await auth.login(email, password);
      if (res.vault_id) {
        goto(`/vaults/${res.vault_id}/dashboard`);
      } else {
        goto('/');
      }
    } catch (err: any) {
      error = err.detail ?? 'Login failed';
    } finally {
      submitting = false;
    }
  }
</script>

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
