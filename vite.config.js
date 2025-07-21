import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	// Use environment variable or fallback to GitHub Pages path
	base: process.env.BASE_PATH || '/obbba-scatter'
});
