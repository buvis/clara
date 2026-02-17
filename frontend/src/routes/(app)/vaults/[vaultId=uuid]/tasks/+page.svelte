<script lang="ts">
  import { page } from '$app/state';
  import { tasksApi } from '$api/tasks';
  import type { TaskCreateInput } from '$api/tasks';
  import DataList from '$components/data/DataList.svelte';
  import Button from '$components/ui/Button.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Input from '$components/ui/Input.svelte';
  import { Plus, CheckCircle, Circle, CheckSquare } from 'lucide-svelte';
  import type { Task } from '$lib/types/models';

  const vaultId = $derived(page.params.vaultId);

  let showCreate = $state(false);
  let createForm = $state<TaskCreateInput>({ title: '' });
  let creating = $state(false);
  let listKey = $state(0);

  const filters = [
    { label: 'Pending', value: 'pending' },
    { label: 'In Progress', value: 'in_progress' },
    { label: 'Done', value: 'done' },
    { label: 'Overdue', value: 'overdue' }
  ];

  async function loadTasks(params: { offset: number; limit: number; search: string; filter: string | null }) {
    return tasksApi.list(vaultId, {
      search: params.search || undefined,
      status: params.filter === 'overdue' ? undefined : params.filter ?? undefined,
      overdue: params.filter === 'overdue' ? true : undefined,
      offset: params.offset,
      limit: params.limit
    });
  }

  async function handleCreate() {
    if (!createForm.title.trim()) return;
    creating = true;
    try {
      await tasksApi.create(vaultId, createForm);
      showCreate = false;
      createForm = { title: '' };
      listKey++;
    } finally {
      creating = false;
    }
  }

  async function toggleComplete(task: Task) {
    const newStatus = task.status === 'done' ? 'pending' : 'done';
    await tasksApi.update(vaultId, task.id, { status: newStatus });
    listKey++;
  }

  function formatDate(d: string | null | undefined): string {
    if (!d) return '';
    return new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  }

  const priorityLabels: Record<number, string> = { 0: 'None', 1: 'Low', 2: 'Medium', 3: 'High' };
</script>

<svelte:head><title>Tasks</title></svelte:head>

<div class="space-y-4">
  {#key listKey}
    <DataList
      load={loadTasks}
      {filters}
      searchPlaceholder="Search tasks..."
      emptyIcon={CheckSquare}
      emptyTitle="No tasks yet"
    >
      {#snippet header()}
        <Button onclick={() => (showCreate = true)}><Plus size={16} /> Add Task</Button>
      {/snippet}
      {#snippet row(item: Task)}
        <div class="flex items-center gap-3 px-4 py-3">
          <button onclick={() => toggleComplete(item)} class="shrink-0 text-neutral-400 hover:text-brand-400">
            {#if item.status === 'done'}
              <CheckCircle size={20} class="text-brand-400" />
            {:else}
              <Circle size={20} />
            {/if}
          </button>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium {item.status === 'done' ? 'text-neutral-400 line-through' : 'text-white'}">{item.title}</p>
            {#if item.description}<p class="truncate text-xs text-neutral-500">{item.description}</p>{/if}
          </div>
          <div class="flex items-center gap-2">
            {#if item.due_date}<span class="text-xs text-neutral-500">{formatDate(item.due_date)}</span>{/if}
            {#if item.priority > 0}
              <Badge variant={item.priority >= 3 ? 'danger' : item.priority === 2 ? 'warning' : 'default'} text={priorityLabels[item.priority] ?? `P${item.priority}`} />
            {/if}
          </div>
        </div>
      {/snippet}
    </DataList>
  {/key}
</div>

{#if showCreate}
  <Modal title="New Task" onclose={() => (showCreate = false)}>
    <form onsubmit={handleCreate} class="space-y-4">
      <Input label="Title" bind:value={createForm.title} required />
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Description</label>
        <textarea bind:value={createForm.description} rows="3" class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500"></textarea>
      </div>
      <Input label="Due date" type="date" bind:value={createForm.due_date} />
      <div>
        <label class="mb-1 block text-sm font-medium text-neutral-300">Priority</label>
        <select bind:value={createForm.priority} class="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white outline-none transition focus:border-brand-500">
          <option value={0}>None</option>
          <option value={1}>Low</option>
          <option value={2}>Medium</option>
          <option value={3}>High</option>
        </select>
      </div>
      <div class="flex justify-end gap-3">
        <Button variant="ghost" onclick={() => (showCreate = false)}>Cancel</Button>
        <Button type="submit" loading={creating}>Create</Button>
      </div>
    </form>
  </Modal>
{/if}
