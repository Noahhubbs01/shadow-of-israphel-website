(() => {
  'use strict';
  const media = window.SOI_MEDIA || {};
  const navLinks = [...document.querySelectorAll('.main-nav a')];
  const sections = navLinks.map(link => document.querySelector(link.getAttribute('href')));
  let scrollQueued = false;
  function updateNavigation() {
    let current = 0;
    sections.forEach((section, index) => {
      if (section && section.getBoundingClientRect().top <= 130) current = index;
    });
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 30) current = sections.length - 1;
    navLinks.forEach((link, index) => {
      link.classList.toggle('is-active', index === current);
      if (index === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    scrollQueued = false;
  }
  window.addEventListener('scroll', () => {
    if (!scrollQueued) { requestAnimationFrame(updateNavigation); scrollQueued = true; }
  }, { passive: true });
  updateNavigation();

  const trailer = media.trailer || {};
  if (trailer.src) {
    const player = document.querySelector('#trailer-player');
    const poster = document.querySelector('#trailer-poster');
    const video = document.createElement('video');
    video.controls = true;
    video.playsInline = true;
    video.preload = 'metadata';
    video.setAttribute('aria-label', 'Shadow of Israphel gameplay trailer');
    video.tabIndex = 0;
    if (trailer.poster) video.poster = trailer.poster;
    video.src = trailer.src;
    video.textContent = 'Your browser cannot play this video.';
    const fallback = document.createElement('a');
    fallback.href = trailer.src;
    fallback.className = 'media-fallback';
    fallback.textContent = 'Open the trailer directly';
    fallback.hidden = true;
    video.addEventListener('error', () => { fallback.hidden = false; });
    player.append(video, fallback);
    if (trailer.poster) {
      const backdrop = document.createElement('img');
      backdrop.src = trailer.poster;
      backdrop.alt = '';
      backdrop.className = 'trailer-backdrop';
      poster.querySelector('.poster-scene').replaceChildren(backdrop);
      poster.classList.add('has-footage');
    }
    const launch = document.createElement('button');
    launch.type = 'button';
    launch.className = 'trailer-launch';
    launch.setAttribute('aria-label', 'Play the Shadow of Israphel development trailer');
    const strip = poster.querySelector('.trailer-soon');
    strip.querySelector('span').textContent = 'WATCH THE TRAILER';
    strip.setAttribute('aria-hidden', 'true');
    const playIcon = document.createElement('span');
    playIcon.className = 'trailer-play-icon';
    playIcon.setAttribute('aria-hidden', 'true');
    playIcon.textContent = '▶';
    launch.append(playIcon);
    poster.append(launch);
    launch.addEventListener('click', () => {
      poster.hidden = true;
      player.hidden = false;
      video.focus({ preventScroll: true });
      video.play().catch(() => { /* Native controls remain available if playback needs another gesture. */ });
    });
    document.querySelector('#trailer-caption').textContent = trailer.caption || 'Gameplay trailer';
  }

  const screenshots = (Array.isArray(media.screenshots) ? media.screenshots : []).filter(shot => shot && shot.src);
  if (!screenshots.length) return;
  const grid = document.querySelector('#screenshot-grid');
  const dialog = document.querySelector('#lightbox');
  const fullImage = document.querySelector('#lightbox-image');
  const caption = document.querySelector('#lightbox-caption');
  const count = document.querySelector('#lightbox-count');
  const previous = document.querySelector('#lightbox-prev');
  const next = document.querySelector('#lightbox-next');
  let currentShot = 0;
  let previousOverflow = '';
  let openedFrom = null;

  function showShot(index) {
    currentShot = (index + screenshots.length) % screenshots.length;
    const shot = screenshots[currentShot];
    fullImage.src = shot.src;
    fullImage.alt = shot.alt || shot.caption || `Screenshot ${currentShot + 1}`;
    caption.textContent = shot.caption || '';
    count.textContent = `${String(currentShot + 1).padStart(2, '0')} / ${String(screenshots.length).padStart(2, '0')}`;
  }
  function openShot(index, trigger) {
    openedFrom = trigger;
    showShot(index);
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dialog.showModal();
  }
  document.querySelector('#lightbox-close').addEventListener('click', () => dialog.close());
  previous.addEventListener('click', () => showShot(currentShot - 1));
  next.addEventListener('click', () => showShot(currentShot + 1));
  previous.hidden = next.hidden = screenshots.length < 2;
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); showShot(currentShot - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); showShot(currentShot + 1); }
  });
  dialog.addEventListener('click', event => {
    const bounds = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    if (openedFrom) openedFrom.focus({ preventScroll: true });
  });
  fullImage.addEventListener('error', () => {
    caption.textContent = 'This image could not be loaded. Try the next screenshot.';
  });
  grid.replaceChildren();
  screenshots.forEach((shot, index) => {
    const figure = document.createElement('figure');
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'screenshot-button';
    button.setAttribute('aria-label', `View ${shot.caption || `screenshot ${index + 1}`} full size`);
    const thumbnail = document.createElement('img');
    thumbnail.src = shot.thumbnail || shot.src;
    thumbnail.alt = shot.alt || shot.caption || `Screenshot ${index + 1}`;
    thumbnail.loading = 'lazy';
    thumbnail.decoding = 'async';
    button.append(thumbnail);
    button.addEventListener('click', () => openShot(index, button));
    const label = document.createElement('figcaption');
    const number = document.createElement('span');
    number.textContent = String(index + 1).padStart(2, '0');
    label.append(number, document.createTextNode(shot.caption || `From the adventure ${index + 1}`));
    figure.append(button, label);
    grid.append(figure);
  });
  document.querySelector('#gallery-status').textContent = `${screenshots.length} IN-GAME CAPTURES`;
  document.querySelector('#gallery-intro').textContent = 'Select a screenshot for a closer look.';
})();
