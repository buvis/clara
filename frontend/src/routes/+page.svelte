<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$state/auth.svelte';
  import { api } from '$api/client';
  import Spinner from '$components/ui/Spinner.svelte';
  import type { Vault } from '$lib/types/models';

  let error = $state('');

  $effect(() => {
    resolve();
  });

  async function resolve() {
    try {
      await auth.fetchMe();
    } catch {
      goto('/auth/login');
      return;
    }

    if (!auth.isAuthenticated) {
      goto('/auth/login');
      return;
    }

    try {
      const vaults = await api.get<Vault[]>('/vaults');
      if (vaults.length > 0) {
        goto(`/vaults/${vaults[0].id}/dashboard`);
      } else {
        error = 'No vaults found. Create one first.';
      }
    } catch {
      goto('/auth/login');
    }
  }
</script>

<div class="flex min-h-screen items-center justify-center bg-neutral-950">
  {#if error}
    <p class="text-sm text-neutral-500">{error}</p>
  {:else}
    <Spinner />
  {/if}
</div>
