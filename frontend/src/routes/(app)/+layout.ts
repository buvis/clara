import { redirect } from '@sveltejs/kit';
import { auth } from '$state/auth.svelte';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async () => {
  if (auth.loading) {
    await auth.fetchMe();
  }

  if (!auth.isAuthenticated) {
    redirect(302, '/auth/login');
  }
};
