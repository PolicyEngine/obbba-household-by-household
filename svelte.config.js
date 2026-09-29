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
			base: process.env.BASE_PATH || '/obbba-household-by-household'
		},
		// On Vercel, _app/version.json names the commit it was built from, so the
		// live browser regression run can wait for the deployment it was
		// triggered by (.github/workflows/e2e-live.yml). Elsewhere: a timestamp.
		version: {
			name: process.env.VERCEL_GIT_COMMIT_SHA
		}
	}
};

export default config;