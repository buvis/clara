<script lang="ts">
  import { page } from '$app/state';
  import { giftsApi } from '$api/gifts';
  import type { GiftCreateInput } from '$api/gifts';
  import DataList from '$components/data/DataList.svelte';
  import Button from '$components/ui/Button.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import { Plus, Gift, ExternalLink } from 'lucide-svelte';
  import type { Gift as GiftModel } from '$lib/types/models';
  import { lookup } from '$state/lookup.svelte';

  const vaultId = $derived(page.params.vaultId!);

  let showCreate = $state(false);
  let createForm = $state<GiftCreateInput>({ contact_id: '', direction: 'idea', name: '' });
  let creating = $state(false);
  let listKey = $state(0);

  const filters = [
    { label: 'Given', value: 'given' },
    { label: 'Received', value: 'received' },
    { label: 'Ideas', value: 'idea' }
  ];

  async function loadGifts(params: { offset: number; limit: number; search: string; filter: string | null }) {
    return giftsApi.list(vaultId, {
      search: params.search || undefined,
      direction: params.filter ?? undefined,
      offset: params.offset,
      limit: params.limit
    });
  }

  async function handleCreate() {
    if (!createForm.name.trim()) return;
    creating = true;
    try {
      await giftsApi.create(vaultId, createForm);
      showCreate = false;
      createForm = { contact_id: '', direction: 'idea', name: '' };
      listKey++;
    } finally {
      creating = false;
    }
  }
</script>

<svelte:head><title>Gifts</title></svelte:head>

<div class="space-y-4">
  {#key listKey}
    <DataList
      load={loadGifts}
      {filters}
      searchPlaceholder="Search gifts..."
      emptyIcon={Gift}
      emptyTitle="No gifts yet"
    >
      {#snippet header()}
        <Button onclick={() => (showCreate = true)}><Plus size={16} /> Add Gift</Button>
      {/snippet}
      {#snippet row(item: GiftModel)}
        <div class="flex items-center gap-3 px-4 py-3">
          <Gift size={20} class="shrink-0 text-neutral-400" />
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <p class="truncate text-sm font-medium text-white">{item.name}</p>
              {#if item.link}
                <a href={item.link} target="_blank" rel="noopener noreferrer" class="text-brand-400 hover:text-brand-300"><ExternalLink size={12} /></a>
              {/if}
            </div>
            {#if item.description}<p class="truncate text-xs text-neutral-500">{item.description}</p>{/if}
          </div>
          <div class="flex items-center gap-2">
            {#if item.amount}<span class="text-sm font-medium text-neutral-300">{item.currency} {item.amount}</span>{/if}
            <Badge variant={item.direction === 'given' ? 'success' : 'default'} text={item.direction} />
          </div>
        </div>
      {/snippet}
    </DataList>
  {/key}
</div>

{#if showCreate}
  <Modal title="New Gift" onclose={() => (showCreate = false)}>
    <form onsubmit={handleCreate} class="space-y-4">
      <Input label="Name" bind:value={createForm.name} required />
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Direction</label>
        <select bind:value={createForm.direction} class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500">
          <option value="idea">Idea</option>
          <option value="given">Given</option>
          <option value="received">Received</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Contact</label>
        <select bind:value={createForm.contact_id} required class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500">
          <option value="">Select contact...</option>
          {#each lookup.contacts as c}
            <option value={c.id}>{c.name}</option>
          {/each}
        </select>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <Input label="Amount" type="number" step="0.01" bind:value={createForm.amount} />
        <Input label="Currency" bind:value={createForm.currency} placeholder="USD" />
      </div>
      <Input label="Link" bind:value={createForm.link} placeholder="https://" />
      <div class="flex justify-end gap-3">
        <Button variant="ghost" onclick={() => (showCreate = false)}>Cancel</Button>
        <Button type="submit" loading={creating}>Create</Button>
      </div>
    </form>
  </Modal>
{/if}
