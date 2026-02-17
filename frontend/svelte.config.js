import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ fallback: '200.html' }),
    alias: {
      $api: 'src/lib/api',
      $state: 'src/lib/state',
      $components: 'src/lib/components'
    }
  }
};

export default config;
