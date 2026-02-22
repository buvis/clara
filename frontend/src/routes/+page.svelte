<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$state/auth.svelte';
  import Spinner from '$components/ui/Spinner.svelte';

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

    goto('/vaults');
  }
</script>

<div class="flex min-h-screen items-center justify-center bg-neutral-950">
  <Spinner />
</div>
