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
  var PIXEL_VALUE = 500; // avg AED per lead — used for pixel attribution weighting
  var CURRENCY = 'AED';

  function genEventId() {
    return 'e_' + Date.now() + '_' + Math.random().toString(36).slice(2, 10);
  }

  function safe(s, max) {
    if (s == null) return '';
    return String(s).trim().substring(0, max || 100);
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
    VALUE: PIXEL_VALUE,
    CURRENCY: CURRENCY
  };
})();
