<script lang="ts">
  import { page } from '$app/state';
  import { vaultState } from '$state/vault.svelte';
  import {
    Home,
    Users,
    CheckSquare,
    BookOpen,
    Bell,
    Gift,
    DollarSign,
    Folder,
    Settings
  } from 'lucide-svelte';

  let { onnavigate }: { onnavigate?: () => void } = $props();

  const navItems = [
    { label: 'Dashboard', icon: Home, path: 'dashboard' },
    { label: 'Contacts', icon: Users, path: 'contacts' },
    { label: 'Tasks', icon: CheckSquare, path: 'tasks' },
    { label: 'Journal', icon: BookOpen, path: 'journal' },
    { label: 'Reminders', icon: Bell, path: 'reminders' },
    { label: 'Gifts', icon: Gift, path: 'gifts' },
    { label: 'Debts', icon: DollarSign, path: 'debts' },
    { label: 'Files', icon: Folder, path: 'files' },
    { label: 'Settings', icon: Settings, path: 'settings' }
  ];

  let basePath = $derived(
    vaultState.currentId ? `/vaults/${vaultState.currentId}` : ''
  );

  function isActive(itemPath: string): boolean {
    return page.url.pathname.includes(`/${itemPath}`);
  }
</script>

<nav class="flex h-full w-64 flex-col border-r border-neutral-800 bg-neutral-900">
  <div class="flex h-14 items-center border-b border-neutral-800 px-4">
    <a href="/" class="text-lg font-bold tracking-tight text-white" onclick={onnavigate}>
      CLARA
    </a>
  </div>

  <div class="flex-1 overflow-y-auto py-3">
    <ul class="space-y-0.5 px-2">
      {#each navItems as item}
        {@const active = isActive(item.path)}
        <li>
          <a
            href="{basePath}/{item.path}"
            onclick={onnavigate}
            class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition
              {active
                ? 'bg-brand-500/10 text-brand-400 font-medium'
                : 'text-neutral-400 hover:bg-neutral-800 hover:text-white'}"
          >
            <item.icon size={18} />
            {item.label}
          </a>
        </li>
      {/each}
    </ul>
  </div>
</nav>
