/* Progressive enhancements. All media and navigation also work without JS. */
(() => {
  'use strict';
  document.querySelectorAll('.trailer-frame').forEach(frame => {
    const video = frame.querySelector('video');
    const launch = frame.querySelector('.trailer-launch');
    const error = frame.parentElement.querySelector('.video-error');
    if (!video || !launch) return;
    video.controls = false;
    launch.hidden = false;
    launch.addEventListener('click', () => {
      launch.hidden = true;
      video.controls = true;
      video.focus({ preventScroll: true });
      video.play().catch(() => { if (error) error.hidden = false; });
    });
    video.addEventListener('play', () => {
      video.controls = true;
      launch.hidden = true;
      if (error) error.hidden = true;
    });
    video.addEventListener('error', () => { if (error) error.hidden = false; });
    video.querySelector('source')?.addEventListener('error', () => { if (error) error.hidden = false; });
  });

  const links = [...document.querySelectorAll('.screenshot-link')];
  const dialog = document.querySelector('#lightbox');
  if (!links.length || !dialog || typeof dialog.showModal !== 'function') return;
  const image = dialog.querySelector('#lightbox-image');
  const caption = dialog.querySelector('#lightbox-caption');
  const count = dialog.querySelector('#lightbox-count');
  const original = dialog.querySelector('#lightbox-original');
  let current = 0;
  let opener;
  let overflow = '';

  function show(index) {
    current = (index + links.length) % links.length;
    const link = links[current];
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    caption.textContent = link.dataset.caption;
    count.textContent = `${current + 1} / ${links.length}`;
    original.href = link.href;
  }
  links.forEach((link, index) => {
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      opener = link;
      show(index);
      overflow = document.body.style.overflow;
      dialog.showModal();
      document.body.style.overflow = 'hidden';
    });
  });
  dialog.querySelector('#lightbox-close').addEventListener('click', () => dialog.close());
  dialog.querySelector('#lightbox-prev').addEventListener('click', () => show(current - 1));
  dialog.querySelector('#lightbox-next').addEventListener('click', () => show(current + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      show(current + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
  dialog.addEventListener('click', event => {
    const bounds = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = overflow;
    opener?.focus({ preventScroll: true });
  });
  image.addEventListener('error', () => { caption.textContent = 'The image could not load. Try the original image link below.'; });
})();
