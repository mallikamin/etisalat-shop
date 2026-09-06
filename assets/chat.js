/*!
 * Golden Numbers UAE — website live chat widget (2026-09-05).
 *
 * Replaces the site's WhatsApp CTAs. Bilal answers from the CRM; the visitor never leaves the page.
 *
 * TWO JOBS:
 *   1. Render the chat bubble/panel and talk to the worker.
 *   2. Intercept ANY remaining `a[href*="wa.me"]` click and open the chat instead. This is the
 *      safety net: 4,247 generated number pages plus ~87 hand-written ones carry WhatsApp CTAs,
 *      and a missed one would silently keep sending customers to WhatsApp. Behaviour is correct
 *      the moment this script loads, even where the button still says "WhatsApp".
 *
 * D1 DISCIPLINE (the worker's budget depends on this file behaving):
 *   - No network call on page load. None. The greeting is local; a session row is only created
 *     when the visitor actually sends a message.
 *   - Polling runs ONLY while the panel is open AND the tab is visible.
 *   - Cadence backs off 4s -> 15s -> 60s as the chat goes quiet, and STOPS after 15 minutes.
 *     A tab left open overnight costs nothing.
 *   - No typing indicators, no presence, no read receipts.
 * Do not add a poll on page load, a heartbeat, or an "is an agent online" check. Those are what
 * blew the read cap on 2026-09-04.
 */
(function () {
  'use strict';
  if (window.__gnChatLoaded) return;
  window.__gnChatLoaded = true;

  var API = 'https://bilal-sales.mallikamiin.workers.dev';
  var LS_TOKEN = 'gn_chat_token';
  var LS_SEEN = 'gn_chat_seen_id';
  var LS_LOG = 'gn_chat_log';

  // Poll cadence. Index into these by how long the chat has been quiet.
  var FAST_MS = 4000, MED_MS = 15000, SLOW_MS = 60000, CLOSED_MS = 20000;
  var MED_AFTER_MS = 60000, SLOW_AFTER_MS = 5 * 60000, STOP_AFTER_MS = 15 * 60000;
  // If nobody has replied this long after the visitor's first message, offer the callback form.
  var UNANSWERED_MS = 3 * 60000;

  var isAr = (document.documentElement.lang || '').toLowerCase().indexOf('ar') === 0;
  var T = isAr ? {
    title: 'الدعم المباشر', sub: 'نرد عليك هنا',
    greet: 'أهلاً بك 👋 اسأل عن أي رقم أو باقة — سنرد عليك هنا مباشرة.',
    ph: 'اكتب رسالتك…', send: 'إرسال', cta: 'تحدث معنا',
    cbTitle: 'اطلب مكالمة', cbLead: 'اترك رقمك وسيتصل بك المختص.',
    cbPhone: 'رقمك (الإمارات)', cbTime: 'أفضل وقت للاتصال', cbSend: 'اطلب مكالمة',
    cbDone: '✅ شكراً لك. سيتصل بك المختص في الوقت المحدد.',
    slots: { now: '📞 اتصلوا بي الآن', '9am-1pm': '٩ ص – ١ م', '1pm-5pm': '١ م – ٥ م', '5pm-9pm': '٥ م – ٩ م' },
    err: 'تعذر الإرسال. حاول مرة أخرى.', offline: 'اترك رقمك وسنتصل بك.'
  } : {
    title: 'Live support', sub: 'We reply right here',
    greet: 'Hi 👋 Ask about any number or plan — we answer you right here.',
    ph: 'Type your message…', send: 'Send', cta: 'Chat with us',
    cbTitle: 'Request a call', cbLead: 'Leave your number and our specialist will call you.',
    cbPhone: 'Your UAE mobile number', cbTime: 'Best time to call', cbSend: 'Request a call',
    cbDone: '✅ Thank you. Our specialist will call you at your chosen time.',
    slots: { now: '📞 Call me now', '9am-1pm': '9 AM – 1 PM', '1pm-5pm': '1 PM – 5 PM', '5pm-9pm': '5 PM – 9 PM' },
    err: 'Could not send. Please try again.', offline: 'Leave your number and we will call you.'
  };

  var token = null, lastId = 0, open = false, timer = null, log = [], unread = 0;
  var firstSentAt = 0, lastActivityAt = Date.now(), answered = false, cbShown = false, cbDone = false;
  var lastSeed = '';   // the last CTA-supplied prefill, so a newer CTA may replace it

  try { token = localStorage.getItem(LS_TOKEN) || null; } catch (e) {}
  try { lastId = parseInt(localStorage.getItem(LS_SEEN) || '0', 10) || 0; } catch (e) {}
  try { log = JSON.parse(localStorage.getItem(LS_LOG) || '[]') || []; } catch (e) { log = []; }

  function save() {
    try {
      if (token) localStorage.setItem(LS_TOKEN, token);
      localStorage.setItem(LS_SEEN, String(lastId));
      localStorage.setItem(LS_LOG, JSON.stringify(log.slice(-40)));
    } catch (e) {}
  }

  // The GN attribution token that assets/tracking.js builds, when that script is present.
  function ref() {
    try {
      if (window.GN && typeof window.GN.currentRef === 'function') return String(window.GN.currentRef() || '');
      var m = document.querySelector('a[data-gn-token]');
      if (m) return String(m.getAttribute('data-gn-token') || '');
    } catch (e) {}
    return '';
  }

  // ---- styles -------------------------------------------------------------
  var css = ''
    // --gnc-bottom lets a page lift the bubble clear of its own fixed furniture. The 3,207
    // /numbers/ pages carry a full-width sticky contact bar at bottom:0, and without this the
    // bubble sat directly on top of that bar's own CTA.
    + '.gnc-btn{position:fixed;bottom:var(--gnc-bottom,18px);' + (isAr ? 'left' : 'right') + ':18px;z-index:99998;'
    + 'display:flex;align-items:center;gap:.5rem;background:#0b7a4b;color:#fff;border:0;cursor:pointer;'
    + 'padding:.8rem 1.15rem;border-radius:999px;font:600 15px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif;'
    + 'box-shadow:0 6px 22px rgba(0,0,0,.28)}'
    + '.gnc-btn:hover{background:#0a6a41}'
    + '.gnc-btn .gnc-dot{width:8px;height:8px;border-radius:50%;background:#7CFFB2}'
    + '.gnc-wrap{position:fixed;bottom:var(--gnc-bottom,18px);' + (isAr ? 'left' : 'right') + ':18px;z-index:99999;width:352px;max-width:calc(100vw - 24px);'
    + 'background:#fff;border-radius:16px;overflow:hidden;display:none;flex-direction:column;'
    + 'box-shadow:0 18px 50px rgba(0,0,0,.3);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;'
    + 'direction:' + (isAr ? 'rtl' : 'ltr') + '}'
    // Every colour below is stated explicitly. The widget sits on pages whose body text is near
    // white on a near-black theme, and the first build inherited that: the greeting rendered as
    // pale grey on a white bubble and was unreadable (Malik, screenshot 2026-09-05). A widget
    // must never inherit the host page's text colour.
    + '.gnc-wrap,.gnc-wrap *{color:#1b1b1b;box-sizing:border-box}'
    + '.gnc-wrap.gnc-open{display:flex}'
    + '.gnc-hd{background:#0b7a4b;padding:.85rem 1rem;display:flex;align-items:center;justify-content:space-between}'
    + '.gnc-hd,.gnc-hd *{color:#fff}'
    + '.gnc-hd b{font-size:15px}.gnc-hd small{opacity:.85;display:block;font-size:12px}'
    + '.gnc-x{background:transparent;border:0;font-size:22px;line-height:1;cursor:pointer;padding:0 .25rem}'
    + '.gnc-body{padding:.9rem;height:330px;overflow-y:auto;background:#f6f7f9}'
    + '.gnc-m{max-width:82%;padding:.55rem .75rem;border-radius:12px;margin-bottom:.5rem;white-space:pre-wrap;word-wrap:break-word;font-size:14px}'
    + '.gnc-m.them{background:#fff;border:1px solid #e6e8eb;color:#1b1b1b;' + (isAr ? 'margin-left:auto' : 'margin-right:auto') + '}'
    + '.gnc-m.me,.gnc-m.me *{background:#0b7a4b;color:#fff;' + (isAr ? 'margin-right:auto' : 'margin-left:auto') + '}'
    // Unread badge on the closed bubble.
    + '.gnc-badge{background:#dc2626;color:#fff;border-radius:999px;min-width:19px;height:19px;'
    + 'display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;padding:0 5px}'
    + '.gnc-m.sys{background:#fff7e6;border:1px solid #ffe2ab;color:#7a4b00;max-width:100%;font-size:13px}'
    + '.gnc-ft{display:flex;align-items:flex-end;gap:.5rem;padding:.6rem;border-top:1px solid #e6e8eb;background:#fff}'
    + '.gnc-ft textarea{flex:1;border:1px solid #d7dade;border-radius:10px;padding:.6rem .7rem;'
    + 'font:inherit;min-width:0;resize:none;max-height:132px;overflow-y:auto;line-height:1.4}'
    + '.gnc-ft button{background:#0b7a4b;color:#fff;border:0;border-radius:10px;padding:.6rem .9rem;font:600 14px/1 inherit;cursor:pointer}'
    + '.gnc-cb{padding:.85rem;border-top:1px solid #e6e8eb;background:#fff}'
    + '.gnc-cb b{display:block;margin-bottom:.15rem}'
    + '.gnc-cb p{margin:0 0 .55rem;color:#5b6470;font-size:13px}'
    + '.gnc-cb input,.gnc-cb select{width:100%;box-sizing:border-box;border:1px solid #d7dade;border-radius:10px;padding:.55rem .65rem;font:inherit;margin-bottom:.5rem}'
    + '.gnc-cb button{width:100%;background:#c8a24a;color:#1b1b1b;border:0;border-radius:10px;padding:.65rem;font:700 14px/1 inherit;cursor:pointer}'
    + '@media (max-width:420px){.gnc-wrap{bottom:0;' + (isAr ? 'left' : 'right') + ':0;width:100vw;max-width:100vw;border-radius:14px 14px 0 0}.gnc-body{height:52vh}}';

  var styleEl = document.createElement('style');
  styleEl.textContent = css;

  var btn, wrap, bodyEl, inputEl, cbEl;

  function el(tag, cls, html) {
    var d = document.createElement(tag);
    if (cls) d.className = cls;
    if (html != null) d.innerHTML = html;
    return d;
  }

  function build() {
    document.head.appendChild(styleEl);

    btn = el('button', 'gnc-btn');
    btn.type = 'button';
    btn.setAttribute('aria-label', T.cta);
    btn.appendChild(el('span', 'gnc-dot'));
    btn.appendChild(document.createTextNode(T.cta));
    btn.addEventListener('click', function () { toggle(true); });

    wrap = el('div', 'gnc-wrap');
    wrap.setAttribute('role', 'dialog');
    wrap.setAttribute('aria-label', T.title);

    var hd = el('div', 'gnc-hd');
    hd.appendChild(el('div', null, '<b>' + T.title + '</b><small>' + T.sub + '</small>'));
    var x = el('button', 'gnc-x', '&times;');
    x.type = 'button';
    x.setAttribute('aria-label', 'Close');
    x.addEventListener('click', function () { toggle(false); });
    hd.appendChild(x);

    bodyEl = el('div', 'gnc-body');

    var ft = el('div', 'gnc-ft');
    // A textarea, not an <input>. An <input> silently strips newlines from its value, so the
    // checkout summary (number / plan / name / mobile / address / call slot, one per line)
    // collapsed into one unreadable run-on sentence the moment it was prefilled.
    inputEl = document.createElement('textarea');
    inputEl.rows = 1;
    inputEl.placeholder = T.ph;
    inputEl.setAttribute('aria-label', T.ph);
    // Enter sends, Shift+Enter makes a new line — the convention every messenger uses.
    inputEl.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
    });
    inputEl.addEventListener('input', autoGrow);
    var sb = el('button', null, T.send);
    sb.type = 'button';
    sb.addEventListener('click', send);
    ft.appendChild(inputEl);
    ft.appendChild(sb);

    wrap.appendChild(hd);
    wrap.appendChild(bodyEl);
    wrap.appendChild(ft);
    document.body.appendChild(btn);
    document.body.appendChild(wrap);

    if (!log.length) push('them', T.greet, true);
    else log.forEach(function (m) { render(m.role, m.body); });
  }

  function render(role, body) {
    var cls = role === 'customer' ? 'me' : (role === 'system' ? 'sys' : 'them');
    var d = el('div', 'gnc-m ' + cls);
    d.textContent = body;
    bodyEl.appendChild(d);
    bodyEl.scrollTop = bodyEl.scrollHeight;
  }

  function push(role, body, ephemeral) {
    render(role === 'me' ? 'customer' : role, body);
    if (!ephemeral) { log.push({ role: role === 'me' ? 'customer' : role, body: body }); save(); }
  }

  function toggle(on) {
    open = !!on;
    wrap.classList.toggle('gnc-open', open);
    btn.style.display = open ? 'none' : '';
    if (open) { unread = 0; paintBadge(); lastActivityAt = Date.now(); schedule(); inputEl.focus(); }
    else schedule();   // NOT stop(): keep watching quietly so the badge can appear (see below)
  }

  // Unread signal. A reply that lands while the panel is shut, or while the visitor is on another
  // tab, was previously invisible — they had to guess and reopen. Now the bubble carries a count
  // and the tab title changes, which is the only way a backgrounded visitor learns we answered.
  function paintBadge() {
    if (!btn) return;
    var b = btn.querySelector('.gnc-badge');
    if (unread > 0) {
      if (!b) { b = el('span', 'gnc-badge'); btn.appendChild(b); }
      b.textContent = unread > 9 ? '9+' : String(unread);
    } else if (b) {
      b.parentNode.removeChild(b);
    }
    var base = document.title.replace(/^\(\d+\+?\)\s*/, '');
    document.title = unread > 0 ? '(' + (unread > 9 ? '9+' : unread) + ') ' + base : base;
  }

  // ---- network ------------------------------------------------------------
  function post(path, payload) {
    return fetch(API + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(function (r) { return r.json().then(function (j) { return { status: r.status, json: j }; }); });
  }

  function send() {
    var text = (inputEl.value || '').trim();
    if (!text) return;
    inputEl.value = '';
    lastSeed = '';
    autoGrow();
    push('me', text);
    lastActivityAt = Date.now();
    if (!firstSentAt) firstSentAt = Date.now();
    post('/api/chat/send', {
      token: token, body: text, ref: ref(),
      page_url: location.pathname.slice(0, 300), company: '',
    }).then(function (r) {
      if (r.status === 200 && r.json && r.json.token) {
        token = r.json.token;
        if (r.json.id) lastId = Math.max(lastId, r.json.id);
        save();
        schedule();
      } else if (r.status === 503 || (r.json && r.json.error === 'chat off')) {
        showCallback(true);
      } else if (r.status !== 200) {
        showOffline();
      }
    }).catch(function () {
      showOffline();
    });
    maybeOfferCallbackLater();
  }

  function poll() {
    // NOTE: deliberately no `!open` guard. A closed panel still watches, slowly, so a reply can
    // raise the unread badge. `document.hidden` still stops everything — a backgrounded tab must
    // cost nothing — and visibilitychange re-arms on return.
    if (!token || document.hidden) return;
    fetch(API + '/api/chat/poll?t=' + encodeURIComponent(token) + '&after=' + lastId)
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var msgs = (j && j.messages) || [];
        for (var i = 0; i < msgs.length; i++) {
          var m = msgs[i];
          lastId = Math.max(lastId, m.id);
          if (m.role === 'customer') continue;            // our own, already on screen
          answered = true;
          lastActivityAt = Date.now();
          push(m.role === 'agent' ? 'them' : 'system', m.body);
          if (!open) { unread++; }
        }
        if (msgs.length) paintBadge();
        save();
      })
      .catch(function () {})
      .then(function () { schedule(); });
  }

  // Cadence: fast while the conversation is live, slower as it goes quiet, stopped when stale.
  function interval() {
    var quiet = Date.now() - lastActivityAt;
    if (quiet > STOP_AFTER_MS) return 0;
    if (quiet > SLOW_AFTER_MS) return SLOW_MS;
    if (quiet > MED_AFTER_MS) return MED_MS;
    return FAST_MS;
  }

  function schedule() {
    stop();
    if (!token || document.hidden) return;
    var ms = interval();
    if (!ms) return;                                       // gone stale: stop entirely
    // Closed panel: watch, but slowly. 20s is fast enough for a badge to feel responsive and, at
    // ~2 rows read per poll, cheap enough that a visitor idling with the panel shut for the whole
    // 15-minute window costs about 90 rows against a 5,000,000/day budget.
    if (!open) ms = Math.max(ms, CLOSED_MS);
    timer = setTimeout(poll, ms);
  }

  function stop() { if (timer) { clearTimeout(timer); timer = null; } }

  // Any interaction re-arms a stopped poller.
  ['click', 'keydown'].forEach(function (evt) {
    document.addEventListener(evt, function () {
      if (open && !timer) { lastActivityAt = Date.now(); schedule(); }
    }, { passive: true });
  });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else if (open) { lastActivityAt = Date.now(); schedule(); }
  });

  // ---- callback fallback --------------------------------------------------
  // Nobody is guaranteed to be at the CRM. If no reply arrives, ask for the same two things the
  // WhatsApp form asks for, so the lead is never lost to an unattended chat.
  function maybeOfferCallbackLater() {
    setTimeout(function () { if (!answered && !cbDone) showCallback(false); }, UNANSWERED_MS);
  }

  // Hard fallback for when the backend cannot answer AT ALL (2026-09-05: D1's daily read cap was
  // exhausted and every chat endpoint errored, including the callback form, which also needs the
  // database). A customer must never be left staring at a dead box. This path touches no backend:
  // it just shows the phone number as a tap-to-call link, so the lead is still reachable.
  function showOffline() {
    if (document.querySelector('.gnc-offline')) return;
    var d = el('div', 'gnc-cb gnc-offline');
    d.appendChild(el('b', null, isAr ? 'اتصل بنا مباشرة' : 'Please call us'));
    d.appendChild(el('p', null, isAr
      ? 'الدردشة غير متاحة مؤقتاً. اتصل بنا وسنساعدك فوراً.'
      : 'Chat is temporarily unavailable. Call us and we will help you right away.'));
    var a = document.createElement('a');
    a.href = 'tel:+971569028087';
    a.textContent = '📞 056 902 8087';
    a.style.cssText = 'display:block;text-align:center;background:#0b7a4b;color:#fff;'
      + 'padding:.7rem;border-radius:10px;font-weight:700;text-decoration:none';
    d.appendChild(a);
    wrap.appendChild(d);
    var body = wrap.querySelector('.gnc-body');
    if (body) body.scrollTop = body.scrollHeight;
  }

  function showCallback(force) {
    if (cbShown || cbDone) return;
    if (!token && !force) return;
    cbShown = true;
    cbEl = el('div', 'gnc-cb');
    cbEl.appendChild(el('b', null, T.cbTitle));
    cbEl.appendChild(el('p', null, T.cbLead));
    var ph = document.createElement('input');
    ph.type = 'tel'; ph.placeholder = T.cbPhone; ph.setAttribute('aria-label', T.cbPhone);
    var sel = document.createElement('select');
    sel.setAttribute('aria-label', T.cbTime);
    ['now', '9am-1pm', '1pm-5pm', '5pm-9pm'].forEach(function (k) {
      var o = document.createElement('option');
      o.value = k; o.textContent = T.slots[k];
      sel.appendChild(o);
    });
    var go = el('button', null, T.cbSend);
    go.type = 'button';
    go.addEventListener('click', function () {
      var digits = (ph.value || '').replace(/\D/g, '');
      if (!/^(?:00971|971|0)?5\d{8}$/.test(digits)) { ph.style.borderColor = '#c00'; return; }
      go.disabled = true;
      post('/api/chat/callback', { token: token, phone: digits, slot: sel.value, company: '' })
        .then(function (r) {
          if (r.status === 200) {
            cbDone = true;
            cbEl.parentNode && cbEl.parentNode.removeChild(cbEl);
            push('system', T.cbDone);
          } else {
            // The callback form needs the database too, so when the backend is down this fails
            // as well. Fall through to the phone number rather than leaving a dead button.
            go.disabled = false;
            showOffline();
          }
        })
        .catch(function () { go.disabled = false; showOffline(); });
    });
    cbEl.appendChild(ph);
    cbEl.appendChild(sel);
    cbEl.appendChild(go);
    wrap.appendChild(cbEl);
  }

  // ---- WhatsApp CTA interception -----------------------------------------
  // The safety net described at the top of this file. Capture phase + preventDefault, so the
  // browser never follows the link and tracking.js's href rewrite cannot navigate us away.
  //
  // 2026-09-06: this used to also call ev.stopPropagation(). That killed every analytics
  // handler on the site. stopPropagation during the document-level CAPTURE phase stops the
  // event before it ever reaches the target, so it never bubbles back to document — and the
  // GA4 / Meta / TikTok listeners on this site are all delegated bubble-phase listeners on
  // document. Every CTA click was silently unattributed. preventDefault alone does the job:
  // it cancels the navigation without cancelling anyone else's bookkeeping.
  function interceptWa(ev) {
    var t = ev.target;
    if (!t || typeof t.closest !== 'function') return;
    var a = t.closest('a[href*="wa.me"], a[href*="api.whatsapp.com"], a[data-gn-chat]');
    if (!a) return;
    ev.preventDefault();
    // Pages that used to hand off to WhatsApp built a message naming the number and plan.
    // Keep that context: prefill it so the visitor only has to press Send. Kept synchronous
    // on purpose — openChat() focuses the input, and iOS only raises the keyboard for a
    // focus() that happens inside the user gesture. Every CTA therefore carries its
    // data-gn-msg in the markup, rather than relying on a handler to fill it in first.
    openChat(a.getAttribute('data-gn-msg') || '');
  }

  // Public hook for pages that opened WhatsApp from script rather than from a link — a
  // window.open cannot be intercepted, so those call sites call this directly.
  // Grow the composer to fit its content, up to the max-height the stylesheet sets.
  function autoGrow() {
    if (!inputEl) return;
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 132) + 'px';
  }

  function openChat(prefill) {
    toggle(true);
    if (!prefill || !inputEl) return;
    // Replace a previous seed, never something the visitor typed. Picking card A, closing the
    // panel and then picking card B must show B's number, not A's.
    if (inputEl.value && inputEl.value !== lastSeed) return;
    lastSeed = String(prefill).slice(0, 400);
    inputEl.value = lastSeed;
    autoGrow();
    inputEl.focus();
  }

  function init() {
    build();
    window.gnOpenChat = openChat;
    // A returning visitor who already has a conversation starts watching straight away, so a
    // reply sent while they were gone shows as a badge instead of staying invisible until they
    // happen to reopen the panel. Visitors who have never chatted have no token and cost nothing.
    if (token) schedule();
    document.addEventListener('click', interceptWa, true);
    document.addEventListener('auxclick', interceptWa, true);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
