/* ═══════════════════════════════════════════════════════════════
   FRONTIER MOTO - index.js

   Five jobs, nothing else: theme toggle, the pinned header, the
   mobile menu overlay, the staggered reveal, and the demo forms.
   There is no runtime content rendering; pages ship as real HTML.
   ═══════════════════════════════════════════════════════════════ */

document.documentElement.classList.add('js');

(function () {
    'use strict';

    var root = document.documentElement;
    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ── 1. THEME ─────────────────────────────────────────────────
    // The attribute is already set by the inline script in <head> so the page
    // never paints the wrong palette. This only wires the toggle.

    var themeToggle = document.getElementById('theme-toggle');

    function reflectTheme(theme) {
        if (!themeToggle) return;
        var toDark = theme !== 'dark';
        themeToggle.setAttribute('aria-label', toDark ? 'Switch to dark theme' : 'Switch to light theme');
        themeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    }

    reflectTheme(root.getAttribute('data-theme') || 'light');

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            var next = (root.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            try { localStorage.setItem('frontier-theme', next); } catch (e) { /* private mode */ }
            reflectTheme(next);
        });
    }

    // ── 2. PINNED HEADER ─────────────────────────────────────────
    // A one pixel sentinel at the top of the document rather than a scroll
    // listener. When it leaves the viewport the header takes its compact,
    // solid state, which is also what makes it legible over dark hero art.

    var header = document.querySelector('.site-header');
    var sentinel = document.getElementById('header-sentinel');

    var headerReported = false;

    if (header && sentinel && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
            headerReported = true;
            header.classList.toggle('is-pinned', !entries[0].isIntersecting);
        }, { threshold: 0 }).observe(sentinel);

        // A working observer always reports once immediately, so no report at all
        // means the rendering lifecycle is not running for this document. Left
        // alone the header would stay transparent with light type, and end up
        // over a bone coloured section further down the page. Pin it instead.
        window.setTimeout(function () {
            if (!headerReported) header.classList.add('is-pinned');
        }, 1200);
    } else if (header) {
        header.classList.add('is-pinned');
    }

    // ── 3. MENU OVERLAY ──────────────────────────────────────────
    // Full screen, focus trapped while open, focus restored to the trigger on
    // close. The Market action lives in the header rather than in here, so
    // supply is one tap away without opening a menu.

    var trigger = document.getElementById('menu-trigger');
    var overlay = document.getElementById('menu-overlay');
    var lastFocused = null;

    var FOCUSABLE = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';

    function focusableIn(el) {
        return Array.prototype.filter.call(el.querySelectorAll(FOCUSABLE), function (node) {
            return node.offsetParent !== null || node.getClientRects().length > 0;
        });
    }

    function openMenu() {
        lastFocused = document.activeElement;
        overlay.classList.add('is-open');
        overlay.removeAttribute('inert');
        document.body.classList.add('menu-open');
        trigger.setAttribute('aria-expanded', 'true');
        var first = focusableIn(overlay)[0];
        if (first) first.focus();
    }

    function closeMenu() {
        overlay.classList.remove('is-open');
        document.body.classList.remove('menu-open');
        trigger.setAttribute('aria-expanded', 'false');
        // Deferred so the element is not hidden from AT mid transition.
        window.setTimeout(function () {
            if (!overlay.classList.contains('is-open')) overlay.setAttribute('inert', '');
        }, 320);
        if (lastFocused && lastFocused.focus) lastFocused.focus();
    }

    if (trigger && overlay) {
        overlay.setAttribute('inert', '');
        trigger.addEventListener('click', function () {
            overlay.classList.contains('is-open') ? closeMenu() : openMenu();
        });

        var closeBtn = overlay.querySelector('[data-menu-close]');
        if (closeBtn) closeBtn.addEventListener('click', closeMenu);

        Array.prototype.forEach.call(overlay.querySelectorAll('a'), function (link) {
            link.addEventListener('click', closeMenu);
        });

        document.addEventListener('keydown', function (e) {
            if (!overlay.classList.contains('is-open')) return;

            if (e.key === 'Escape') {
                e.preventDefault();
                closeMenu();
                return;
            }

            if (e.key !== 'Tab') return;

            var items = focusableIn(overlay);
            if (!items.length) return;
            var first = items[0];
            var last = items[items.length - 1];

            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        });

        // A width change that reveals the desktop nav should not leave a
        // full screen overlay stranded on top of the page.
        window.matchMedia('(min-width: 1151px)').addEventListener('change', function (e) {
            if (e.matches && overlay.classList.contains('is-open')) closeMenu();
        });
    }

    // ── 3b. MORE MENU ────────────────────────────────────────────
    // One disclosure holding Workshop and Field Notes, so the header stays six
    // Index sections plus the Market action. Click toggles, Escape closes and
    // returns focus, a pointer down outside closes. No animation beyond the
    // global transition, which reduced motion already neutralises.

    Array.prototype.forEach.call(document.querySelectorAll('[data-more]'), function (box) {
        var button = box.querySelector('.more__button');
        if (!button) return;

        function closeMore(refocus) {
            box.removeAttribute('data-open');
            button.setAttribute('aria-expanded', 'false');
            if (refocus && button.focus) button.focus();
        }

        button.addEventListener('click', function () {
            var open = box.getAttribute('data-open') === 'true';
            if (open) {
                closeMore(false);
            } else {
                box.setAttribute('data-open', 'true');
                button.setAttribute('aria-expanded', 'true');
            }
        });

        document.addEventListener('click', function (e) {
            if (box.getAttribute('data-open') === 'true' && !box.contains(e.target)) {
                closeMore(false);
            }
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && box.getAttribute('data-open') === 'true') {
                e.preventDefault();
                closeMore(true);
            }
        });
    });

    // ── 4. STAGGERED REVEAL ──────────────────────────────────────
    // Stagger comes from the --i custom property in the markup, not from JS
    // timing. Under reduced motion everything is shown at once and no
    // observer is constructed at all.

    var revealEls = document.querySelectorAll('[data-reveal]');

    function revealAll() {
        Array.prototype.forEach.call(revealEls, function (el) { el.classList.add('is-visible'); });
    }

    if (prefersReduced || !('IntersectionObserver' in window)) {
        revealAll();
    } else {
        var revealReported = false;

        // These elements start at opacity 0, so an observer that never reports
        // would leave the page permanently blank. Same failsafe as the header:
        // no report at all means show everything rather than hide the site.
        window.setTimeout(function () {
            if (!revealReported) revealAll();
        }, 1200);

        var observer = new IntersectionObserver(function (entries, obs) {
            revealReported = true;
            entries.forEach(function (entry) {
                // An element taller than the viewport can never reach a 0.15
                // ratio, so a long article body would sit at opacity 0 forever.
                var viewport = window.innerHeight || document.documentElement.clientHeight;
                var tall = entry.boundingClientRect.height > viewport;
                var ready = tall ? entry.isIntersecting : entry.intersectionRatio >= 0.15;
                if (ready) {
                    entry.target.classList.add('is-visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: [0, 0.15] });

        Array.prototype.forEach.call(revealEls, function (el) { observer.observe(el); });
    }

    // ── 5. DEMO FORMS ────────────────────────────────────────────
    // Nothing here has a backend. The forms validate and report properly so
    // they are usable and accessible, and then say plainly that the entry was
    // not transmitted. Making that obvious in the behaviour is the point.

    Array.prototype.forEach.call(document.querySelectorAll('[data-demo-form]'), function (form) {
        var status = form.querySelector('.form-status');
        var submit = form.querySelector('[type="submit"]');

        function setFieldError(field, message) {
            var wrap = field.closest('.field');
            if (!wrap) return;
            var slot = wrap.querySelector('.field__error');
            if (message) {
                wrap.setAttribute('data-invalid', 'true');
                field.setAttribute('aria-invalid', 'true');
                if (slot) slot.textContent = message;
            } else {
                wrap.removeAttribute('data-invalid');
                field.removeAttribute('aria-invalid');
                if (slot) slot.textContent = '';
            }
        }

        Array.prototype.forEach.call(form.querySelectorAll('input, select, textarea'), function (field) {
            field.addEventListener('input', function () { setFieldError(field, ''); });
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            var invalid = null;
            Array.prototype.forEach.call(form.querySelectorAll('input, select, textarea'), function (field) {
                if (field.checkValidity()) {
                    setFieldError(field, '');
                } else {
                    var message = field.validity.valueMissing
                        ? 'This is needed before the request makes sense.'
                        : (field.validationMessage || 'Check this entry.');
                    setFieldError(field, message);
                    if (!invalid) invalid = field;
                }
            });

            if (invalid) {
                if (status) {
                    status.setAttribute('data-state', 'error');
                    status.textContent = 'Some entries still need attention. The first one is highlighted below.';
                }
                invalid.focus();
                return;
            }

            if (submit) {
                submit.setAttribute('data-loading', 'true');
                submit.setAttribute('aria-disabled', 'true');
            }

            window.setTimeout(function () {
                if (submit) {
                    submit.removeAttribute('data-loading');
                    submit.removeAttribute('aria-disabled');
                }
                if (status) {
                    status.setAttribute('data-state', 'ok');
                    status.textContent = form.getAttribute('data-demo-message')
                        || 'This form is a front end demonstration. Nothing was sent and no one has been notified.';
                }
            }, prefersReduced ? 0 : 520);
        });
    });
})();
