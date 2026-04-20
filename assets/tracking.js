/**
 * goldennummbers.com unified tracking helper.
 * Centralizes GA4 + Meta Pixel + TikTok Pixel events with deduplication event_id.
 * Loaded on every page after gtag/fbq/ttq init scripts.
 *
 * Functions:
 *   GN.genEventId()                                    → unique id for pixel/GA4/CAPI dedup
 *   GN.trackWhatsAppClick(ctx, pageContext)            → every wa.me click
 *   GN.trackNumberInquiry({number, category, ref, leadToken})  → /choose-number wa clicks
 *   GN.trackLead({source, interest, value})            → form submits, signups
 *   GN.trackPartnerScan(refCode)                       → QR partner scans
 */
(function () {
  'use strict';
  var PIXEL_ID = '1456083435966506';
  var PIXEL_VALUE = 500; // avg AED per lead — used for pixel attribution weighting
  var CURRENCY = 'AED';

  function genEventId() {
    return 'e_' + Date.now() + '_' + Math.random().toString(36).slice(2, 10);
  }

  function safe(s, max) {
    if (s == null) return '';
    return String(s).trim().substring(0, max || 100);
  }

  function normalizePhone(raw) {
    if (!raw) return '';
    var digits = String(raw).replace(/[^0-9]/g, '');
    if (!digits) return '';
    if (digits.charAt(0) === '0') digits = '971' + digits.slice(1);
    if (digits.length === 9) digits = '971' + digits;
    return digits;
  }

  function splitName(full) {
    if (!full) return { fn: '', ln: '' };
    var parts = String(full).trim().split(/\s+/);
    return { fn: (parts[0] || '').toLowerCase(), ln: (parts.slice(1).join(' ') || '').toLowerCase() };
  }

  /**
   * Manual Advanced Matching — enriches the pixel with hashed user identity
   * so Meta can match events to user accounts (improves match rate 20-30%).
   * Call this BEFORE firing a pixel event (e.g., on form submit) with whatever
   * identity fields you have. Meta auto-hashes client-side via SHA-256.
   * Pass any subset of {email, phone, name, city, country, zip, gender, dob, externalId}.
   */
  function setUserIdentity(opts) {
    opts = opts || {};
    if (typeof fbq !== 'function') return;
    var data = {};
    if (opts.email)   data.em = String(opts.email).trim().toLowerCase();
    if (opts.phone)   data.ph = normalizePhone(opts.phone);
    if (opts.name) {
      var n = splitName(opts.name);
      if (n.fn) data.fn = n.fn;
      if (n.ln) data.ln = n.ln;
    }
    if (opts.firstName) data.fn = String(opts.firstName).trim().toLowerCase();
    if (opts.lastName)  data.ln = String(opts.lastName).trim().toLowerCase();
    if (opts.city)      data.ct = String(opts.city).trim().toLowerCase().replace(/\s+/g, '');
    if (opts.country)   data.country = String(opts.country).trim().toLowerCase();
    if (opts.zip)       data.zp = String(opts.zip).trim();
    if (opts.gender)    data.ge = String(opts.gender).charAt(0).toLowerCase();
    if (opts.dob)       data.db = String(opts.dob).replace(/[^0-9]/g, '').slice(0, 8);
    if (opts.externalId) data.external_id = String(opts.externalId);
    if (!Object.keys(data).length) return;
    try { fbq('init', PIXEL_ID, data); } catch (e) {}
  }

  function trackWhatsAppClick(ctx, pageContext) {
    var eid = genEventId();
    var category = safe(ctx, 50) || 'cta';
    var page = safe(pageContext, 50) || (typeof location !== 'undefined' ? location.pathname : '');
    if (typeof fbq === 'function') {
      fbq('track', 'Contact', {
        content_name: 'WhatsApp Click',
        content_category: category,
        value: PIXEL_VALUE,
        currency: CURRENCY
      }, { eventID: eid });
    }
    if (typeof ttq !== 'undefined' && ttq.track) {
      ttq.track('Contact', {
        content_name: 'WhatsApp Click',
        content_category: category
      });
    }
    if (typeof gtag === 'function') {
      gtag('event', 'contact', {
        cta_context: category,
        page_context: page,
        event_id: eid
      });
    }
    return eid;
  }

  function trackNumberInquiry(opts) {
    opts = opts || {};
    var num = safe(opts.number, 30);
    var cat = safe(opts.category, 20) || 'unknown';
    var ref = safe(opts.ref, 30);
    var eid = opts.leadToken || genEventId();
    if (typeof fbq === 'function') {
      fbq('track', 'Contact', {
        content_name: 'Number Inquiry',
        content_category: cat,
        content_ids: [num],
        value: PIXEL_VALUE,
        currency: CURRENCY
      }, { eventID: eid });
    }
    if (typeof ttq !== 'undefined' && ttq.track) {
      ttq.track('Contact', {
        content_name: 'Number Inquiry',
        content_category: cat,
        content_ids: [num]
      });
    }
    if (typeof gtag === 'function') {
      gtag('event', 'number_inquiry', {
        number_id: num,
        number_category: cat,
        ref_code: ref,
        lead_token: eid,
        event_id: eid
      });
    }
    return eid;
  }

  function trackLead(opts) {
    opts = opts || {};
    var source = safe(opts.source, 30) || 'unknown';
    var interest = safe(opts.interest, 50);
    var eid = opts.eventId || genEventId();
    var value = opts.value || PIXEL_VALUE;
    if (typeof fbq === 'function') {
      fbq('track', 'Lead', {
        content_name: source,
        content_category: interest,
        value: value,
        currency: CURRENCY
      }, { eventID: eid });
    }
    if (typeof ttq !== 'undefined' && ttq.track) {
      ttq.track('SubmitForm', {
        content_name: source,
        content_category: interest
      });
    }
    if (typeof gtag === 'function') {
      gtag('event', 'generate_lead', {
        lead_source: source,
        interest_type: interest,
        value: value,
        currency: CURRENCY,
        event_id: eid
      });
    }
    return eid;
  }

  function trackPartnerScan(refCode) {
    var ref = safe(refCode, 30);
    var eid = genEventId();
    if (typeof gtag === 'function') {
      gtag('event', 'partner_scan', {
        ref_code: ref,
        event_id: eid
      });
    }
    if (typeof fbq === 'function') {
      fbq('trackCustom', 'PartnerScan', { ref_code: ref }, { eventID: eid });
    }
    return eid;
  }

  window.GN = {
    genEventId: genEventId,
    trackWhatsAppClick: trackWhatsAppClick,
    trackNumberInquiry: trackNumberInquiry,
    trackLead: trackLead,
    trackPartnerScan: trackPartnerScan,
    setUserIdentity: setUserIdentity,
    VALUE: PIXEL_VALUE,
    CURRENCY: CURRENCY,
    PIXEL_ID: PIXEL_ID
  };
})();
