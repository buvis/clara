<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$state/auth.svelte';
  import { vaultState } from '$state/vault.svelte';
  import { Menu, LogOut, ChevronDown } from 'lucide-svelte';

  let { ontogglesidebar }: { ontogglesidebar: () => void } = $props();

  let userMenuOpen = $state(false);

  async function handleLogout() {
    await auth.logout();
    goto('/auth/login');
  }

  function handleVaultChange(e: Event) {
    const select = e.target as HTMLSelectElement;
    const vault = vaultState.vaults.find((v) => v.id === select.value);
    if (vault) {
      vaultState.setCurrent(vault);
      goto(`/vaults/${vault.id}/dashboard`);
    }
  }
</script>

<header class="flex h-14 shrink-0 items-center justify-between border-b border-neutral-800 bg-neutral-900 px-4">
  <div class="flex items-center gap-3">
    <button
      class="rounded-lg p-1.5 text-neutral-400 hover:bg-neutral-800 hover:text-white lg:hidden"
      onclick={ontogglesidebar}
      aria-label="Toggle sidebar"
    >
      <Menu size={20} />
    </button>

    <!-- Vault selector -->
    {#if vaultState.vaults.length > 0}
      <div class="relative">
        <select
          value={vaultState.currentId ?? ''}
          onchange={handleVaultChange}
          class="appearance-none rounded-lg border border-neutral-700 bg-neutral-800 py-1.5 pl-3 pr-8 text-sm text-white outline-none transition focus:border-brand-500"
        >
          {#each vaultState.vaults as vault}
            <option value={vault.id}>{vault.name}</option>
          {/each}
        </select>
        <ChevronDown
          size={14}
          class="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-neutral-400"
        />
      </div>
    {/if}
  </div>

  <div class="relative">
    <button
      onclick={() => (userMenuOpen = !userMenuOpen)}
      class="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm text-neutral-300 transition hover:bg-neutral-800 hover:text-white"
    >
      <span class="flex h-7 w-7 items-center justify-center rounded-full bg-brand-500/20 text-xs font-medium text-brand-400">
        {auth.user?.name?.charAt(0).toUpperCase() ?? '?'}
      </span>
      <span class="hidden sm:inline">{auth.user?.name ?? 'User'}</span>
      <ChevronDown size={14} />
    </button>

    {#if userMenuOpen}
      <button
        class="fixed inset-0 z-40"
        onclick={() => (userMenuOpen = false)}
        aria-label="Close menu"
      ></button>
      <div class="absolute right-0 z-50 mt-1 w-48 rounded-lg border border-neutral-700 bg-neutral-800 py-1 shadow-xl">
        <div class="border-b border-neutral-700 px-3 py-2">
          <p class="text-sm text-white">{auth.user?.name}</p>
          <p class="text-xs text-neutral-400">{auth.user?.email}</p>
        </div>
        <button
          onclick={handleLogout}
          class="flex w-full items-center gap-2 px-3 py-2 text-sm text-neutral-300 transition hover:bg-neutral-700 hover:text-white"
        >
          <LogOut size={14} />
          Sign out
        </button>
      </div>
    {/if}
  </div>
</header>
