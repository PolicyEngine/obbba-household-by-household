<script>
  import { base } from '$app/paths';

  // PolicyEngine site shell, rendered by the child app itself. Multizone
  // rewrites proxy this app under policyengine.org/us/obbba-household-explorer
  // but do not inject the parent site shell, so the header/nav and footer are
  // rendered here. Both routes are full-viewport apps, so the header is fixed
  // and pages size themselves against --pe-shell-height.
  const NAV_LINKS = [
    { label: 'Working paper', href: `${base}/paper/` },
    { label: 'Research', href: 'https://policyengine.org/us/research' },
    { label: 'Model', href: 'https://policyengine.org/us/model' },
    { label: 'API', href: 'https://policyengine.org/us/api' },
    { label: 'Donate', href: 'https://policyengine.org/us/donate' }
  ];

  const FOOTER_LINKS = [
    { label: 'About us', href: 'https://policyengine.org/us/team' },
    { label: 'Donate', href: 'https://policyengine.org/us/donate' },
    { label: 'Developer tools', href: 'https://policyengine.org/us/dev-tools' },
    { label: 'Privacy policy', href: 'https://policyengine.org/us/privacy' },
    { label: 'Terms and conditions', href: 'https://policyengine.org/us/terms' }
  ];
</script>

<nav class="pe-shell-header" aria-label="PolicyEngine site header">
  <div class="pe-shell-row">
    <a class="pe-shell-brand" href="https://policyengine.org/us" aria-label="PolicyEngine home">
      <img src="{base}/policyengine-white.svg" alt="PolicyEngine" />
    </a>
    <div class="pe-shell-links">
      {#each NAV_LINKS as link}
        <a href={link.href}>{link.label}</a>
      {/each}
    </div>
  </div>
</nav>

<div class="pe-shell-content">
  <slot />
</div>

<footer class="pe-shell-site-footer">
  <div class="pe-shell-foot-inner">
    <nav class="pe-shell-footer" aria-label="PolicyEngine site footer">
      {#each FOOTER_LINKS as link}
        <a href={link.href}>{link.label}</a>
      {/each}
    </nav>
    <p class="pe-shell-copy">&copy; 2026 PolicyEngine</p>
  </div>
</footer>

<style>
  :global(:root) {
    --pe-shell-height: 58px;
  }

  .pe-shell-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 10000;
    height: var(--pe-shell-height);
    background: linear-gradient(to right, #234e52, #2c7a7b);
  }

  .pe-shell-row {
    display: flex;
    align-items: center;
    gap: 32px;
    height: 100%;
    padding: 0 24px;
  }

  .pe-shell-brand {
    display: inline-flex;
    align-items: center;
    flex-shrink: 0;
  }

  .pe-shell-brand img {
    height: 24px;
    width: auto;
    display: block;
  }

  .pe-shell-links {
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .pe-shell-links a {
    font-family: var(--pe-font-family-primary, 'Inter', sans-serif);
    font-size: 15px;
    font-weight: 500;
    color: #fff;
    text-decoration: none;
    transition: opacity 0.15s ease;
  }

  .pe-shell-links a:hover {
    opacity: 0.8;
  }

  .pe-shell-content {
    padding-top: var(--pe-shell-height);
  }

  .pe-shell-site-footer {
    position: relative;
    z-index: 30;
    background: linear-gradient(to right, #234e52, #2c7a7b);
  }

  .pe-shell-foot-inner {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 28px 24px;
  }

  .pe-shell-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 24px;
  }

  .pe-shell-footer a {
    font-family: var(--pe-font-family-primary, 'Inter', sans-serif);
    font-size: 14px;
    font-weight: 500;
    color: #fff;
    text-decoration: none;
    transition: opacity 0.15s ease;
  }

  .pe-shell-footer a:hover {
    opacity: 0.8;
  }

  .pe-shell-copy {
    margin: 0;
    font-family: var(--pe-font-family-primary, 'Inter', sans-serif);
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7);
  }

  @media (max-width: 640px) {
    .pe-shell-row {
      gap: 16px;
      padding: 0 16px;
    }

    .pe-shell-links {
      gap: 14px;
    }

    .pe-shell-links a {
      font-size: 13px;
    }
  }
</style>
