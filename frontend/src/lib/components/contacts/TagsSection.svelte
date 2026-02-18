<script lang="ts">
  import { contactsApi, tagsApi } from '$api/contacts';
  import Button from '$components/ui/Button.svelte';
  import { Plus, X } from 'lucide-svelte';
  import type { Tag } from '$lib/types/models';

  interface Props {
    vaultId: string;
    contactId: string;
  }

  let { vaultId, contactId }: Props = $props();

  let tags = $state<Tag[]>([]);
  let allTags = $state<Tag[]>([]);
  let loading = $state(true);
  let error = $state('');
  let adding = $state(false);
  let selectedTagId = $state('');
  let saving = $state(false);

  $effect(() => {
    Promise.all([
      contactsApi.listTags(vaultId, contactId),
      tagsApi.list(vaultId)
    ]).then(([contactTags, vaultTags]) => {
      tags = contactTags;
      allTags = vaultTags;
      loading = false;
    }).catch(() => {
      error = 'Failed to load tags';
      loading = false;
    });
  });

  let availableTags = $derived(
    allTags.filter((t) => !tags.some((ct) => ct.id === t.id))
  );

  async function handleAdd() {
    if (!selectedTagId) return;
    saving = true;
    try {
      const tag = await contactsApi.addTag(vaultId, contactId, selectedTagId);
      tags = [...tags, tag];
      selectedTagId = '';
      adding = false;
    } finally {
      saving = false;
    }
  }

  async function handleRemove(tagId: string) {
    await contactsApi.removeTag(vaultId, contactId, tagId);
    tags = tags.filter((t) => t.id !== tagId);
  }
</script>

<div class="rounded-lg border border-neutral-800 p-4">
  <div class="mb-3 flex items-center justify-between">
    <h3 class="text-xs font-semibold uppercase tracking-wider text-neutral-500">Tags</h3>
    {#if !adding}
      <button onclick={() => (adding = true)} class="text-neutral-400 hover:text-white">
        <Plus size={16} />
      </button>
    {/if}
  </div>

  {#if error}
    <p class="text-xs text-red-400">{error}</p>
  {:else if loading}
    <p class="text-xs text-neutral-500">Loading...</p>
  {:else if tags.length === 0 && !adding}
    <p class="text-xs text-neutral-500">No tags yet</p>
  {:else}
    <div class="flex flex-wrap gap-1.5">
      {#each tags as tag (tag.id)}
        <span
          class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium"
          style="background-color: {tag.color}20; color: {tag.color}; border: 1px solid {tag.color}40"
        >
          {tag.name}
          <button onclick={() => handleRemove(tag.id)} class="opacity-60 hover:opacity-100">
            <X size={12} />
          </button>
        </span>
      {/each}
    </div>
  {/if}

  {#if adding}
    <form onsubmit={handleAdd} class="mt-2 flex gap-2">
      <select bind:value={selectedTagId} class="min-w-0 flex-1 rounded border border-neutral-700 bg-neutral-800 px-2 py-1 text-xs text-white">
        <option value="">Select a tag...</option>
        {#each availableTags as tag (tag.id)}
          <option value={tag.id}>{tag.name}</option>
        {/each}
      </select>
      <Button size="sm" type="submit" loading={saving} disabled={!selectedTagId}>Add</Button>
      <Button size="sm" variant="ghost" onclick={() => (adding = false)}>Cancel</Button>
    </form>
  {/if}
</div>
