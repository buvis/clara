<script lang="ts">
  import { page } from '$app/state';
  import { activitiesApi } from '$api/activities';
  import type { ActivityCreateInput, ActivityUpdateInput, ParticipantInput } from '$api/activities';
  import DataList from '$components/data/DataList.svelte';
  import Button from '$components/ui/Button.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import { Plus, CalendarDays, Pencil, Trash2 } from 'lucide-svelte';
  import type { Activity } from '$lib/types/models';
  import { lookup } from '$state/lookup.svelte';

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
  let editingActivity = $state<Activity | null>(null);
  let deletingActivity = $state<Activity | null>(null);
  let editForm = $state<ActivityUpdateInput>({});
  let editParticipants = $state<ParticipantInput[]>([]);
  let saving = $state(false);
  let deleting = $state(false);

  $effect(() => {
    lookup.loadContacts(vaultId);
    lookup.loadActivityTypes(vaultId);
  });

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

  function startEdit(activity: Activity) {
    editForm = {
      activity_type_id: activity.activity_type_id,
      title: activity.title,
      description: activity.description,
      happened_at: new Date(activity.happened_at).toISOString().slice(0, 16),
      location: activity.location
    };
    editParticipants = activity.participants?.map(p => ({
      contact_id: p.contact_id,
      role: p.role
    })) ?? [];
    editingActivity = activity;
  }

  async function handleEdit() {
    if (!editingActivity) return;
    saving = true;
    try {
      const data = {
        ...editForm,
        happened_at: new Date(editForm.happened_at!).toISOString(),
        participants: editParticipants
      };
      await activitiesApi.update(vaultId, editingActivity.id, data);
      listKey++;
      editingActivity = null;
    } finally {
      saving = false;
    }
  }

  async function handleDelete() {
    if (!deletingActivity) return;
    deleting = true;
    try {
      await activitiesApi.del(vaultId, deletingActivity.id);
      listKey++;
      deletingActivity = null;
    } finally {
      deleting = false;
    }
  }

  function addParticipant() {
    editParticipants.push({ contact_id: '', role: '' });
  }

  function removeParticipant(index: number) {
    editParticipants = editParticipants.filter((_, i) => i !== index);
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
            <a href={`/vaults/${vaultId}/activities/${item.id}`} class="truncate text-sm font-medium text-white hover:underline">{item.title}</a>
            {#if item.description}
              <p class="truncate text-xs text-neutral-500">{item.description}</p>
            {/if}
            {#if item.location}
              <p class="truncate text-xs text-neutral-500">{item.location}</p>
            {/if}
          </div>
          <span class="shrink-0 text-xs text-neutral-500">{formatDate(item.happened_at)}</span>
          <div class="flex items-center gap-2">
            <button onclick={() => startEdit(item)} class="shrink-0 text-neutral-400 hover:text-neutral-300">
              <Pencil size={14} />
            </button>
            <button onclick={() => (deletingActivity = item)} class="shrink-0 text-neutral-400 hover:text-red-400">
              <Trash2 size={14} />
            </button>
          </div>
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

{#if editingActivity}
  <Modal title="Edit Activity" onclose={() => (editingActivity = null)}>
    <form onsubmit={handleEdit} class="space-y-4">
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Type</label>
        <select bind:value={editForm.activity_type_id} class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500">
          <option value="">No Type</option>
          {#each lookup.activityTypes as t}
            <option value={t.id}>{t.name}</option>
          {/each}
        </select>
      </div>
      <Input label="Title" bind:value={editForm.title} required />
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Description</label>
        <textarea
          bind:value={editForm.description}
          rows="3"
          class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
        ></textarea>
      </div>
      <Input label="Date and time" type="datetime-local" bind:value={editForm.happened_at} required />
      <Input label="Location" bind:value={editForm.location} />

      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Participants</label>
        <div class="space-y-2">
          {#each editParticipants as participant, i}
            <div class="flex gap-2">
              <select bind:value={participant.contact_id} class="flex-1 rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500">
                <option value="">Select contact...</option>
                {#each lookup.contacts as c}
                  <option value={c.id}>{c.name}</option>
                {/each}
              </select>
              <input
                type="text"
                bind:value={participant.role}
                placeholder="Role (optional)"
                class="flex-1 rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              />
              <button type="button" onclick={() => removeParticipant(i)} class="text-neutral-400 hover:text-red-400">
                <Trash2 size={16} />
              </button>
            </div>
          {/each}
          <Button type="button" variant="ghost" size="sm" onclick={addParticipant}>
            <Plus size={14} /> Add Participant
          </Button>
        </div>
      </div>

      <div class="flex justify-end gap-3">
        <Button variant="ghost" onclick={() => (editingActivity = null)}>Cancel</Button>
        <Button type="submit" loading={saving}>Save</Button>
      </div>
    </form>
  </Modal>
{/if}

{#if deletingActivity}
  <Modal title="Delete Activity" onclose={() => (deletingActivity = null)}>
    <p class="text-sm text-neutral-400">Delete <strong>{deletingActivity.title}</strong>? This cannot be undone.</p>
    <div class="mt-4 flex justify-end gap-3">
      <Button variant="ghost" onclick={() => (deletingActivity = null)}>Cancel</Button>
      <Button variant="danger" loading={deleting} onclick={handleDelete}>Delete</Button>
    </div>
  </Modal>
{/if}
