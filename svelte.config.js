import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: 'index.html',
			precompress: false,
			strict: false
		}),
		paths: {
			// Use environment variable or fallback to GitHub Pages path
			base: process.env.BASE_PATH || '/obbba-scatter'
		}
	}
};

export default config;