// Adds `is-revealed` to figures and headline words as they scroll into view, so the
// animations in motion.css run once. Without this script, the 4 s guard in baseof adds
// `no-reveal` to <html> and every figure renders fully drawn.
(function () {
  'use strict';

  if (window.__revealGuard) clearTimeout(window.__revealGuard);

  var targets = Array.prototype.slice.call(document.querySelectorAll('.fig, .rise'));
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function reveal(el) {
    el.classList.add('is-revealed');
  }

  if (reduced || typeof IntersectionObserver === 'undefined') {
    targets.forEach(reveal);
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      reveal(entry.target);
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });

  targets.forEach(function (el) { observer.observe(el); });
})();
