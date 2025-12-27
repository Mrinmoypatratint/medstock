// =========================================
// MOBILE MENU TOGGLE
// =========================================
function initMobileMenu() {
  const menuBtn = document.getElementById('mobileMenuBtn');
  const mobileMenu = document.getElementById('mobileMenu');
  const iconOpen = document.getElementById('menuIconOpen');
  const iconClose = document.getElementById('menuIconClose');

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      const isOpen = !mobileMenu.classList.contains('hidden');
      mobileMenu.classList.toggle('hidden');
      iconOpen?.classList.toggle('hidden');
      iconClose?.classList.toggle('hidden');
      menuBtn.setAttribute('aria-expanded', !isOpen);
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!menuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.add('hidden');
        iconOpen?.classList.remove('hidden');
        iconClose?.classList.add('hidden');
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });

    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
        iconOpen?.classList.remove('hidden');
        iconClose?.classList.add('hidden');
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

// =========================================
// FILTER PANE TOGGLE (Desktop)
// =========================================
// Toggle left filter pane with Tab key (desktop convenience)
document.addEventListener('keydown', (e) => {
  if (e.key === 'Tab' && !e.shiftKey) {
    const pane = document.getElementById('filterPane');
    if (pane) { pane.classList.toggle('hidden'); }
  }
});

// =========================================
// MEDICINE LIST & DETAIL PANE
// =========================================
// Load details into right pane when a list item is clicked
function bindMedListLinks(scope) {
  (scope || document).querySelectorAll('#medList a[data-detail-url]').forEach(a => {
    a.addEventListener('click', async (ev) => {
      ev.preventDefault();
      const url = a.getAttribute('data-detail-url');
      await loadDetail(url);
      
      // On mobile, scroll to detail pane
      if (window.innerWidth < 1024) {
        const pane = document.getElementById('detailPane');
        if (pane) {
          pane.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });
}

async function loadDetail(url) {
  const pane = document.getElementById('detailPane');
  if (!pane) return;
  pane.innerHTML = '<div class="p-4 text-slate-500 flex items-center gap-2"><svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Loading…</div>';
  try {
    const resp = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    pane.innerHTML = await resp.text();
  } catch (err) {
    pane.innerHTML = '<div class="p-4 text-red-500">Failed to load. Please try again.</div>';
  }
}

async function refreshMedList() {
  const list = document.getElementById('medList');
  if (!list) return;
  const q = document.querySelector('input[name="q"]')?.value || '';
  try {
    const resp = await fetch(`/medlist/?q=${encodeURIComponent(q)}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    list.innerHTML = await resp.text();
    bindMedListLinks(list); // re-bind new items
  } catch (err) {
    console.error('Failed to refresh list:', err);
  }
}

function bindDetailPaneActions() {
  const pane = document.getElementById('detailPane');
  if (!pane) return;

  // Load edit form
  pane.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-edit-url],[data-detail-url]');
    if (!btn) return;

    // open edit partial
    if (btn.hasAttribute('data-edit-url')) {
      e.preventDefault();
      const url = btn.getAttribute('data-edit-url');
      await loadDetail(url);
    }
    // go back to detail
    if (btn.hasAttribute('data-detail-url')) {
      e.preventDefault();
      const url = btn.getAttribute('data-detail-url');
      await loadDetail(url);
    }
  });

  // AJAX submit for forms inside pane (edit + delete)
  pane.addEventListener('submit', async (e) => {
    const form = e.target;
    if (!form.matches('form[data-ajax="true"]')) return;
    e.preventDefault();
    
    // Add loading state
    const submitBtn = form.querySelector('button[type="submit"], button:not([type])');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.classList.add('opacity-50');
    }
    
    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      const html = await resp.text();
      pane.innerHTML = html;
      await refreshMedList(); // update the left list after save/delete
    } catch (err) {
      pane.innerHTML = '<div class="p-4 text-red-500">Failed to save. Please try again.</div>';
    }
  });
}

// =========================================
// TOAST NOTIFICATIONS
// =========================================
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// =========================================
// COPY TO CLIPBOARD
// =========================================
function initCopyButtons() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-copy]');
    if (!btn) return;
    e.preventDefault();
    
    const selector = btn.getAttribute('data-copy');
    const el = document.querySelector(selector);
    if (!el) return;
    
    const text = (el.textContent || '').trim();
    if (!text) return;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        // Visual feedback
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        btn.classList.add('bg-green-100', 'text-green-700');
        setTimeout(() => {
          btn.textContent = originalText;
          btn.classList.remove('bg-green-100', 'text-green-700');
        }, 1500);
      });
    }
  });
}

// =========================================
// RESPONSIVE TABLE LABELS
// =========================================
function addMobileTableLabels() {
  document.querySelectorAll('table thead th').forEach((th, index) => {
    const label = th.textContent.trim();
    document.querySelectorAll(`table tbody tr`).forEach(row => {
      const td = row.querySelectorAll('td')[index];
      if (td && label) {
        td.setAttribute('data-label', label);
      }
    });
  });
}

// =========================================
// INITIALIZATION
// =========================================
document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  bindMedListLinks(document);
  bindDetailPaneActions();
  initCopyButtons();
  addMobileTableLabels();
});
