(() => {
  const button = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav-links');
  if (!button || !nav) return;

  const close = (restoreFocus = false) => {
    nav.classList.remove('open');
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-label', 'Open navigation');
    if (restoreFocus) button.focus();
  };

  const open = () => {
    nav.classList.add('open');
    button.setAttribute('aria-expanded', 'true');
    button.setAttribute('aria-label', 'Close navigation');
    const firstLink = nav.querySelector('a');
    if (firstLink) firstLink.focus();
  };

  button.addEventListener('click', () => {
    if (nav.classList.contains('open')) close();
    else open();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) close(true);
  });

  document.addEventListener('click', (event) => {
    if (!nav.classList.contains('open')) return;
    if (!nav.contains(event.target) && !button.contains(event.target)) close();
  });

  nav.addEventListener('click', (event) => {
    if (event.target.closest('a')) close();
  });
})();