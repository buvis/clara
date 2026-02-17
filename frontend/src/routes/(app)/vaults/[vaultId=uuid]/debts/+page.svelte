<script lang="ts">
  import { page } from '$app/state';
  import { debtsApi } from '$api/debts';
  import type { DebtCreateInput } from '$api/debts';
  import DataList from '$components/data/DataList.svelte';
  import Button from '$components/ui/Button.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import { Plus, DollarSign } from 'lucide-svelte';
  import type { Debt } from '$lib/types/models';
  import { lookup } from '$state/lookup.svelte';

  const vaultId = $derived(page.params.vaultId);

  let showCreate = $state(false);
  let createForm = $state<DebtCreateInput>({ contact_id: '', direction: 'you_owe', amount: 0 });
  let creating = $state(false);
  let listKey = $state(0);

  const filters = [
    { label: 'You Owe', value: 'you_owe' },
    { label: 'Owed to You', value: 'owed_to_you' },
    { label: 'Settled', value: 'settled' }
  ];

  async function loadDebts(params: { offset: number; limit: number; search: string; filter: string | null }) {
    return debtsApi.list(vaultId, {
      search: params.search || undefined,
      direction: params.filter === 'settled' ? undefined : params.filter ?? undefined,
      settled: params.filter === 'settled' ? true : undefined,
      offset: params.offset,
      limit: params.limit
    });
  }

  async function handleCreate() {
    if (!createForm.contact_id || createForm.amount <= 0) return;
    creating = true;
    try {
      await debtsApi.create(vaultId, createForm);
      showCreate = false;
      createForm = { contact_id: '', direction: 'you_owe', amount: 0 };
      listKey++;
    } finally {
      creating = false;
    }
  }

  async function toggleSettled(debt: Debt) {
    await debtsApi.update(vaultId, debt.id, { settled: !debt.settled });
    listKey++;
  }
</script>

<svelte:head><title>Debts</title></svelte:head>

<div class="space-y-4">
  {#key listKey}
    <DataList
      load={loadDebts}
      {filters}
      searchPlaceholder="Search debts..."
      emptyIcon={DollarSign}
      emptyTitle="No debts"
    >
      {#snippet header()}
        <Button onclick={() => (showCreate = true)}><Plus size={16} /> Add Debt</Button>
      {/snippet}
      {#snippet row(item: Debt)}
        <div class="flex items-center gap-3 px-4 py-3">
          <DollarSign size={20} class="shrink-0 text-neutral-400" />
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-white">{item.currency} {item.amount}</p>
            <p class="text-xs text-neutral-500">{lookup.getContactName(item.contact_id)}</p>
            {#if item.notes}<p class="truncate text-xs text-neutral-500">{item.notes}</p>{/if}
          </div>
          <div class="flex items-center gap-2">
            <Badge variant={item.direction === 'you_owe' ? 'danger' : 'success'} text={item.direction === 'you_owe' ? 'You owe' : 'Owed to you'} />
            {#if item.settled}
              <Badge variant="success" text="Settled" />
            {:else}
              <Button variant="ghost" size="sm" onclick={() => toggleSettled(item)}>Settle</Button>
            {/if}
          </div>
        </div>
      {/snippet}
    </DataList>
  {/key}
</div>

{#if showCreate}
  <Modal title="New Debt" onclose={() => (showCreate = false)}>
    <form onsubmit={handleCreate} class="space-y-4">
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Direction</label>
        <select bind:value={createForm.direction} class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500">
          <option value="you_owe">You Owe</option>
          <option value="owed_to_you">Owed to You</option>
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
        <Input label="Amount" type="number" step="0.01" min="0.01" bind:value={createForm.amount} required />
        <Input label="Currency" bind:value={createForm.currency} placeholder="USD" />
      </div>
      <Input label="Due date" type="date" bind:value={createForm.due_date} />
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Notes</label>
        <textarea bind:value={createForm.notes} rows="2" class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"></textarea>
      </div>
      <div class="flex justify-end gap-3">
        <Button variant="ghost" onclick={() => (showCreate = false)}>Cancel</Button>
        <Button type="submit" loading={creating}>Create</Button>
      </div>
    </form>
  </Modal>
{/if}
