<script lang="ts">
  import { page } from '$app/state';
  import { activitiesApi } from '$api/activities';
  import type { ActivityCreateInput } from '$api/activities';
  import DataList from '$components/data/DataList.svelte';
  import Button from '$components/ui/Button.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import { Plus, CalendarDays } from 'lucide-svelte';
  import type { Activity } from '$lib/types/models';

  const vaultId = $derived(page.params.vaultId!);

  let showCreate = $state(false);
  let createForm = $state<ActivityCreateInput>({
    title: '',
    description: '',
    happened_at: '',
    location: ''
  });
  let creating = $state(false);
  let listKey = $state(0);

  async function loadActivities(params: { offset: number; limit: number; search: string; filter: string | null }) {
    return activitiesApi.list(vaultId, {
      offset: params.offset,
      limit: params.limit
    });
  }

  async function handleCreate() {
    if (!createForm.title.trim() || !createForm.happened_at) return;
    creating = true;
    try {
      await activitiesApi.create(vaultId, createForm);
      showCreate = false;
      createForm = { title: '', description: '', happened_at: '', location: '' };
      listKey++;
    } finally {
      creating = false;
    }
  }

  function formatDate(value: string): string {
    return new Date(value).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<svelte:head><title>Activities</title></svelte:head>

<div class="space-y-4">
  {#key listKey}
    <DataList
      load={loadActivities}
      searchPlaceholder="Search activities..."
      emptyIcon={CalendarDays}
      emptyTitle="No activities yet"
      emptyDescription="Add your first activity to track important moments"
    >
      {#snippet header()}
        <Button onclick={() => (showCreate = true)}><Plus size={16} /> Add Activity</Button>
      {/snippet}
      {#snippet row(item: Activity)}
        <div class="flex items-start justify-between gap-3 px-4 py-3">
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-white">{item.title}</p>
            {#if item.description}
              <p class="truncate text-xs text-neutral-500">{item.description}</p>
            {/if}
            {#if item.location}
              <p class="truncate text-xs text-neutral-500">{item.location}</p>
            {/if}
          </div>
          <span class="shrink-0 text-xs text-neutral-500">{formatDate(item.happened_at)}</span>
        </div>
      {/snippet}
    </DataList>
  {/key}
</div>

{#if showCreate}
  <Modal title="New Activity" onclose={() => (showCreate = false)}>
    <form onsubmit={handleCreate} class="space-y-4">
      <Input label="Title" bind:value={createForm.title} required />
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Description</label>
        <textarea
          bind:value={createForm.description}
          rows="3"
          class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
        ></textarea>
      </div>
      <Input label="Date and time" type="datetime-local" bind:value={createForm.happened_at} required />
      <Input label="Location" bind:value={createForm.location} />
      <div class="flex justify-end gap-3">
        <Button variant="ghost" onclick={() => (showCreate = false)}>Cancel</Button>
        <Button type="submit" loading={creating}>Create</Button>
      </div>
    </form>
  </Modal>
{/if}
