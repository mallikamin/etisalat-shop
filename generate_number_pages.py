"""
Per-number SEO page generator for goldennummbers.com and uaepremiumnumbers.com.

Fetches the live Google Sheets CSV (same source the /choose-number/ page uses),
parses out every Available Silver/Gold/Platinum number, and writes one static
HTML page per number into /numbers/etisalat-<digits>/index.html plus a hub
index at /numbers/index.html plus a sitemap-numbers.xml.

Per-number content is genuinely unique (pattern analysis + prefix region +
tier value-prop + tailored FAQ), so Google indexes them as distinct pages
rather than near-duplicates. Each page has its own Product / BreadcrumbList /
FAQPage JSON-LD, canonical, OG tags, and a Contact Now WhatsApp CTA with a
prefilled message that names the exact number.

Usage:
    python generate_number_pages.py            # both sites
    python generate_number_pages.py gn         # goldennummbers.com only
    python generate_number_pages.py upn        # uaepremiumnumbers.com only
"""

import csv
import html
import io
import os
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

# Force stdout to UTF-8 so Unicode in any progress prints doesn't crash on cp1252 consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------------------
# Data source — same sheets both /choose-number/ pages consume
# ---------------------------------------------------------------------------
SHEETS = [
    {"id": "1qAw1YQkKEbq-R3LullCBNr0MweGfC2KEO-rot9ff8dw", "gid": "0"},
    {"id": "1Lmfsc-0H0R0hXv0wddktRwisHI74yu9JfrtxPajm9hk", "gid": "0"},
]

ACCEPTED_CATEGORIES = {"gold": "Gold", "silver": "Silver", "platinum": "Platinum"}

TIER_PRICE = {
    "Silver":   {"display": "AED 188", "unit": "/mo plan",      "raw": 188},
    "Gold":     {"display": "AED 500", "unit": "/mo plan",      "raw": 500},
    "Platinum": {"display": "AED 1,000","unit": " · one-time",  "raw": 1000},
}

# Etisalat-assigned prefix families. Used for the "Number breakdown" SEO copy.
PREFIX_INFO = {
    "050": "Etisalat's original mobile prefix, introduced in 1994 — the most recognised series across the UAE and a status marker for long-standing residents.",
    "054": "An Etisalat secondary series launched to support Dubai and Abu Dhabi growth — widely used by business customers in the UAE.",
    "056": "Etisalat's modern prefix block — heavily allocated for postpaid plans and VIP numbers in Dubai, Sharjah and the Northern Emirates.",
    "058": "A newer Etisalat block with fresh ranges still available — popular for businesses choosing their first UAE number.",
}

# ---------------------------------------------------------------------------
# Site configurations
# ---------------------------------------------------------------------------
SITES = {
    "gn": {
        "key": "gn",
        "label": "goldennummbers.com",
        "brand": "Golden Numbers UAE",
        "domain": "goldennummbers.com",
        "base_url": "https://goldennummbers.com",
        "project_dir": r"C:\Users\Malik\desktop\etisalat-shop",
        "wa_number": "971569028087",
        "phone_display": "+971 56 902 8087",
        "ga4": "G-G34631QW03",
        "fb_pixel": "1456083435966506",
        "support_email": "support@etisalat.shop",
        "tagline": "Authorized Etisalat Dealer — VIP Mobile Numbers UAE",
        # Midnight Gold theme
        "theme_color": "#0D1117",
        "css_vars": {
            "bg":       "#0D1117",
            "panel":    "#161B22",
            "panel2":   "#1F2630",
            "border":   "#2A313C",
            "text":     "#E6EDF3",
            "muted":    "#8B949E",
            "gold":     "#C9A962",
            "gold2":    "#E0C58A",
            "silver":   "#C0C0C0",
            "platinum": "#E5E4E2",
            "green":    "#25D366",
        },
        "logo_text_class": "midnight",
    },
    "upn": {
        "key": "upn",
        "label": "uaepremiumnumbers.com",
        "brand": "UAE Premium Numbers",
        "domain": "uaepremiumnumbers.com",
        "base_url": "https://uaepremiumnumbers.com",
        "project_dir": r"C:\ST\Sitara Infotech\uae-premium-numbers",
        "wa_number": "971566999377",
        "phone_display": "+971 56 699 9377",
        "ga4": "__GA4_PLACEHOLDER__",
        "fb_pixel": "__FB_PIXEL_PLACEHOLDER__",
        "support_email": "support@uaepremiumnumbers.com",
        "tagline": "Authorized Etisalat Dealer — Premium Mobile Numbers UAE",
        # Etisalat Red on White
        "theme_color": "#ED1C24",
        "css_vars": {
            "bg":       "#FFFFFF",
            "panel":    "#FFFFFF",
            "panel2":   "#FAFAFA",
            "border":   "#EAEAEA",
            "text":     "#0F0F0F",
            "muted":    "#5A5A5A",
            "gold":     "#ED1C24",
            "gold2":    "#C8102E",
            "silver":   "#8C8C8C",
            "platinum": "#4A4A4A",
            "green":    "#25D366",
        },
        "logo_text_class": "red-white",
    },
}


# ===========================================================================
# 1. FETCH + PARSE
# ===========================================================================
def fetch_csv(sheet):
    base = f"https://docs.google.com/spreadsheets/d/{sheet['id']}"
    urls = [
        f"{base}/gviz/tq?tqx=out:csv&headers=1&gid={sheet['gid']}",
        f"{base}/export?format=csv&gid={sheet['gid']}",
    ]
    last_err = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                text = r.read().decode("utf-8", errors="replace").strip()
            if text and not text.startswith("<!DOCTYPE") and not text.startswith("<html"):
                return text
            last_err = "non-csv response"
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(f"All CSV endpoints failed for sheet {sheet['id']}: {last_err}")


def parse_csv(text):
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return []
    header = [h.strip().lower() for h in rows[0]]

    def idx(name, default):
        return header.index(name) if name in header else default

    i_cat   = idx("category", 1)
    i_msi   = idx("msisdn", 2)
    i_with  = idx("with zero", 3)
    i_no    = idx("without zero", 4)
    i_stat  = idx("status", 5)

    out = []
    for row in rows[1:]:
        if len(row) < 4:
            continue
        cat_raw = (row[i_cat] if i_cat < len(row) else "").strip()
        msi     = (row[i_msi] if i_msi < len(row) else "").strip()
        with_z  = (row[i_with] if i_with < len(row) else "").strip().replace(" ", "")
        no_z    = (row[i_no]   if i_no  < len(row) else "").strip().replace(" ", "")
        stat    = (row[i_stat] if i_stat < len(row) else "").strip().lower()

        if stat != "available":
            continue
        if msi == "MSISDN":
            continue

        cat = ACCEPTED_CATEGORIES.get(cat_raw.lower())
        if not cat:
            continue

        if not with_z and no_z:
            with_z = "0" + no_z
        if not with_z:
            continue

        if not msi:
            if no_z:
                msi = "971" + no_z
            elif len(with_z) == 10 and with_z.startswith("0"):
                msi = "971" + with_z[1:]
        if not msi:
            continue

        digits = with_z
        if len(digits) == 10 and digits.startswith("0"):
            formatted = f"{digits[0:3]} {digits[3:6]} {digits[6:]}"
        else:
            formatted = digits

        out.append({
            "category": cat,
            "msisdn":   msi,
            "formatted": formatted,
            "digits":   digits,
        })
    return out


def load_all_numbers():
    merged = []
    seen = set()
    for s in SHEETS:
        try:
            csv_text = fetch_csv(s)
            for n in parse_csv(csv_text):
                key = n["digits"] or n["msisdn"]
                if not key or key in seen:
                    continue
                seen.add(key)
                merged.append(n)
        except Exception as e:
            print(f"  [warn] sheet {s['id']}: {e}")
    return merged


# ===========================================================================
# 2. PATTERN ANALYSIS (engine that produces unique per-page content)
# ===========================================================================
def analyze(digits):
    """Return a dict of distinctive features detected in this 10-digit number.
    Used to compose unique SEO prose so Google does not flag duplicates."""
    if len(digits) != 10:
        return {"prefix": digits[:3], "patterns": [], "highlight": ""}

    prefix = digits[:3]
    body = digits[3:]            # 7 digits after the prefix
    last4 = digits[-4:]
    last5 = digits[-5:]
    last6 = digits[-6:]

    patterns = []
    score = 0

    # All-same trailing
    for k in (6, 5, 4, 3):
        if len(set(digits[-k:])) == 1:
            patterns.append(f"ends in {k} identical {digits[-1]}s ({digits[-k:]})")
            score += 20 + k * 3
            break

    # All-same anywhere
    for d in set(body):
        if body.count(d) >= 5 and not patterns:
            patterns.append(f"contains {body.count(d)} repeating {d}s")
            score += 12

    # Trailing zeros
    z = 0
    for ch in reversed(digits):
        if ch == "0":
            z += 1
        else:
            break
    if z >= 3:
        patterns.append(f"ends in {z} consecutive zeros — a classic round-number signature")
        score += z * 4

    # Ascending / descending in last 4
    if last4 in ("0123","1234","2345","3456","4567","5678","6789"):
        patterns.append(f"ends with the ascending sequence {last4}")
        score += 25
    if last4 in ("9876","8765","7654","6543","5432","4321","3210"):
        patterns.append(f"ends with the descending sequence {last4}")
        score += 25

    # Palindrome in last 5 / last 4
    if last5 == last5[::-1]:
        patterns.append(f"ends with the palindrome {last5}")
        score += 18
    elif last4 == last4[::-1] and len(set(last4)) > 1:
        patterns.append(f"ends with the palindrome {last4}")
        score += 12

    # Repeating pair (ABAB) or triplet (ABCABC) in tail
    if len(last4) == 4 and last4[:2] == last4[2:] and last4[0] != last4[1]:
        patterns.append(f"ends with the repeating pair {last4} ({last4[:2]}/{last4[:2]})")
        score += 14
    if len(last6) == 6 and last6[:3] == last6[3:] and len(set(last6[:3])) > 1:
        patterns.append(f"ends with the repeating triplet {last6}")
        score += 18

    # AABB pattern in last 4
    if (last4[0] == last4[1] and last4[2] == last4[3]
            and last4[0] != last4[2]):
        patterns.append(f"ends with the AABB block {last4}")
        score += 10

    # Stacked pairs / triples count across full number
    counts = Counter(digits)
    pairs   = sum(1 for v in counts.values() if v == 2)
    triples = sum(1 for v in counts.values() if v == 3)
    quads   = sum(1 for v in counts.values() if v >= 4)
    if quads and not any("identical" in p for p in patterns):
        d = [k for k, v in counts.items() if v >= 4][0]
        patterns.append(f"contains {counts[d]} occurrences of the digit {d}")
        score += counts[d] * 3

    # Numerology sum (Arabic-market appeal)
    s = sum(int(c) for c in digits)
    while s > 9:
        s = sum(int(c) for c in str(s))
    digit_sum_root = s

    return {
        "prefix": prefix,
        "patterns": patterns,
        "score": score,
        "digit_sum_root": digit_sum_root,
        "pairs": pairs,
        "triples": triples,
        "quads": quads,
        "trailing_zeros": z,
        "last4": last4,
    }


# ===========================================================================
# 3. PAGE BUILDERS
# ===========================================================================
def slug_for(num):
    return f"etisalat-{num['digits']}"


def url_for(site, num):
    return f"{site['base_url']}/numbers/{slug_for(num)}/"


def wa_link(site, num):
    if num["category"] == "Platinum":
        msg = (f"Hi, I'm interested in the Platinum number {num['formatted']} "
               f"(AED 1,000) from {site['domain']}")
    else:
        msg = (f"Hi, I'm interested in the {num['category']} number "
               f"{num['formatted']} from {site['domain']}")
    return f"https://wa.me/{site['wa_number']}?text={urllib.parse.quote(msg)}", msg


def seo_intro(num, info):
    """Compose a unique introductory paragraph from detected patterns."""
    parts = []
    parts.append(
        f"Etisalat number <strong>{num['formatted']}</strong> is currently available as a "
        f"{num['category']} VIP listing in the UAE."
    )

    prefix_meta = PREFIX_INFO.get(info["prefix"])
    if prefix_meta:
        parts.append(f"The <strong>{info['prefix']}</strong> prefix — {prefix_meta}")

    if info["patterns"]:
        # Take up to 2 strongest patterns
        focus = info["patterns"][:2]
        if len(focus) == 1:
            parts.append(f"This number {focus[0]}, which makes it instantly memorable in voice and on a business card.")
        else:
            parts.append(f"This number {focus[0]}, and also {focus[1]} — a pattern combination that is unusually scarce in active Etisalat ranges.")
    else:
        parts.append(
            "It carries a clean, easy-to-recall structure that lifts it out of the standard pool — "
            "the kind of number you only have to say once."
        )

    parts.append(
        f"Its digit-sum reduces to <strong>{info['digit_sum_root']}</strong>, "
        f"a detail customers from numerology-conscious markets often consider when choosing a personal number."
    )
    return " ".join(parts)


def tier_block(num, site):
    cat = num["category"]
    tier = TIER_PRICE[cat]
    if cat == "Silver":
        copy = ("Silver numbers are released with Etisalat's entry postpaid plan. You keep the number, "
                "the SIM is delivered the same day inside Dubai, Abu Dhabi and Sharjah, and the plan covers "
                "unlimited UAE local minutes plus a high monthly data allowance.")
    elif cat == "Gold":
        copy = ("Gold numbers come with Etisalat's Gold postpaid plan — international minutes are included, "
                "data is uncapped, and the number itself is reserved against your Emirates ID at the point of sale. "
                "Most Gold numbers move within 48 hours of being listed.")
    else:
        copy = ("Platinum numbers are released individually as a one-time premium purchase. You can attach them to "
                "any active Etisalat postpaid plan, and ownership transfers under your Emirates ID with full Etisalat backing.")
    return tier, copy


def faq_for(num, info):
    """Generate 3 number-specific FAQs (used in body and JSON-LD)."""
    qs = []
    qs.append((
        f"Is the Etisalat number {num['formatted']} still available?",
        (f"Yes — at the time this page was last refreshed the number {num['formatted']} was listed as Available "
         f"in the Etisalat VIP catalogue. Inventory moves quickly, so we recommend confirming on WhatsApp before reserving."),
    ))
    if num["category"] == "Platinum":
        qs.append((
            f"How much does the Platinum number {num['formatted']} cost?",
            (f"Platinum numbers are priced from AED 1,000 as a one-time premium on top of the underlying Etisalat postpaid plan. "
             f"Final pricing depends on pattern strength — message us on WhatsApp at {info['phone_display']} for the live quote."),
        )) if False else qs.append((
            f"How much does the Platinum number {num['formatted']} cost?",
            ("Platinum numbers are priced from AED 1,000 as a one-time premium on top of the underlying Etisalat postpaid plan. "
             "Final pricing depends on pattern strength — message us on WhatsApp for the live quote."),
        ))
    elif num["category"] == "Gold":
        qs.append((
            f"What plan comes with Gold number {num['formatted']}?",
            ("This number is released with Etisalat's Gold postpaid plan at AED 500/month. The plan includes uncapped UAE data, "
             "international minutes, and the number is held under your Emirates ID."),
        ))
    else:
        qs.append((
            f"What plan comes with Silver number {num['formatted']}?",
            ("This number is released with Etisalat's entry postpaid plan from AED 188/month. The plan covers UAE local "
             "minutes, generous data, and the SIM is delivered the same day."),
        ))

    if info["patterns"]:
        qs.append((
            f"Why is {num['formatted']} considered a VIP number?",
            (f"Because it {info['patterns'][0]}. Pattern-rich numbers are easier to remember, project status, and are "
             f"traditionally chosen as business contact lines across the UAE."),
        ))
    else:
        qs.append((
            f"Why is {num['formatted']} considered a VIP number?",
            ("It sits inside Etisalat's curated VIP catalogue — a small, hand-picked pool that Etisalat releases "
             "alongside premium postpaid plans rather than at random allocation."),
        ))
    return qs


def find_related(num, all_numbers, limit_same_tier=4, limit_same_prefix=4):
    same_tier = [n for n in all_numbers
                 if n["category"] == num["category"] and n["digits"] != num["digits"]][:200]
    same_prefix = [n for n in all_numbers
                   if n["digits"][:3] == num["digits"][:3] and n["digits"] != num["digits"]][:200]
    # Rotate based on digit hash so each page lists a different set
    seed = sum(int(c) for c in num["digits"])
    def rotate(arr, k):
        if not arr:
            return []
        k = k % len(arr)
        return (arr[k:] + arr[:k])[:max(limit_same_tier, limit_same_prefix)]
    return rotate(same_tier, seed)[:limit_same_tier], rotate(same_prefix, seed + 7)[:limit_same_prefix]


# ===========================================================================
# 4. HTML TEMPLATE
# ===========================================================================
def page_html(site, num, all_numbers):
    info = analyze(num["digits"])
    info["phone_display"] = site["phone_display"]
    tier, tier_copy = tier_block(num, site)
    rel_tier, rel_prefix = find_related(num, all_numbers)
    wa_href, wa_msg = wa_link(site, num)
    page_url = url_for(site, num)
    faqs = faq_for(num, info)

    css = """:root{
    --bg:__bg__; --panel:__panel__; --panel2:__panel2__; --border:__border__;
    --text:__text__; --muted:__muted__; --gold:__gold__; --gold2:__gold2__;
    --silver:__silver__; --platinum:__platinum__; --green:__green__;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:'DM Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}
  a{color:var(--gold);text-decoration:none}
  a:hover{text-decoration:underline}
  .container{max-width:1100px;margin:0 auto;padding:0 1.25rem}

  /* nav */
  .nav{position:sticky;top:0;z-index:50;background:var(--bg);
       border-bottom:1px solid var(--border);padding:0.9rem 0}
  .nav-inner{display:flex;align-items:center;justify-content:space-between}
  .logo{font-family:'Playfair Display',serif;font-weight:700;font-size:1.35rem;color:var(--gold)}
  .nav-links{display:flex;gap:1.5rem;align-items:center}
  .nav-links a{color:var(--text);font-weight:500;font-size:0.95rem}
  .btn-contact{background:var(--green);color:#fff !important;padding:0.55rem 1.1rem;
               border-radius:999px;font-weight:600;font-size:0.9rem}
  .btn-contact:hover{text-decoration:none;opacity:0.92}

  /* breadcrumb */
  .crumb{font-size:0.85rem;color:var(--muted);padding:1rem 0 0.25rem}
  .crumb a{color:var(--muted)}
  .crumb a:hover{color:var(--gold)}

  /* hero */
  .hero{padding:2rem 0 1rem;text-align:center}
  .tier-pill{display:inline-block;padding:0.35rem 0.95rem;border-radius:999px;
             font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;font-weight:700;margin-bottom:0.9rem}
  .pill-Silver{background:rgba(192,192,192,0.14);color:var(--silver);border:1px solid var(--silver)}
  .pill-Gold{background:rgba(201,169,98,0.14);color:var(--gold);border:1px solid var(--gold)}
  .pill-Platinum{background:rgba(229,228,226,0.14);color:var(--platinum);border:1px solid var(--platinum)}
  h1{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3.2rem);font-weight:700;
     letter-spacing:-0.01em;line-height:1.15;margin-bottom:0.75rem}
  h1 .num{color:var(--gold);font-variant-numeric:tabular-nums;letter-spacing:0.05em;display:block;margin-top:0.35rem;font-size:1.15em}
  .sub{color:var(--muted);font-size:1.05rem;max-width:640px;margin:0 auto 1.5rem}

  .price{font-family:'Playfair Display',serif;font-size:2rem;color:var(--gold);font-weight:600;margin:0.75rem 0 1.25rem}
  .price small{font-size:0.95rem;color:var(--muted);font-weight:400}

  .cta-row{display:flex;justify-content:center;gap:0.75rem;flex-wrap:wrap;margin:1.25rem 0}
  .btn-primary{display:inline-flex;align-items:center;gap:0.55rem;background:var(--green);
               color:#fff;padding:0.95rem 1.6rem;border-radius:999px;font-weight:600;font-size:1.05rem;
               box-shadow:0 8px 22px rgba(37,211,102,0.28)}
  .btn-primary:hover{text-decoration:none;transform:translateY(-1px)}
  .btn-primary svg{width:20px;height:20px}
  .btn-secondary{display:inline-flex;align-items:center;gap:0.55rem;background:transparent;
                 color:var(--text);padding:0.95rem 1.4rem;border-radius:999px;
                 border:1px solid var(--border);font-weight:600;font-size:1.05rem}
  .btn-secondary:hover{text-decoration:none;border-color:var(--gold);color:var(--gold)}

  /* sections */
  .section{padding:2rem 0;border-top:1px solid var(--border)}
  .section h2{font-family:'Playfair Display',serif;font-size:1.6rem;margin-bottom:1rem;color:var(--text)}
  .section p{margin-bottom:0.85rem;color:var(--text)}
  .section p strong{color:var(--gold);font-weight:600}

  /* fact strip */
  .facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0.75rem;margin:1.25rem 0}
  .fact{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:1rem;text-align:center}
  .fact .k{font-size:0.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem}
  .fact .v{font-family:'Playfair Display',serif;font-size:1.4rem;color:var(--gold);font-weight:600}

  /* related grid */
  .related{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:0.75rem;margin-top:1rem}
  .rcard{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:1rem;
         display:flex;flex-direction:column;gap:0.4rem;transition:border-color .15s}
  .rcard:hover{border-color:var(--gold);text-decoration:none}
  .rcard .rnum{font-family:'Playfair Display',serif;font-size:1.2rem;color:var(--gold);font-variant-numeric:tabular-nums;letter-spacing:0.04em}
  .rcard .rmeta{font-size:0.82rem;color:var(--muted)}

  /* faq */
  .faq{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:1rem 1.25rem;margin-bottom:0.75rem}
  .faq h3{font-size:1.05rem;color:var(--text);margin-bottom:0.4rem;font-weight:600}
  .faq p{color:var(--muted);margin:0}

  /* steps */
  .steps{counter-reset:s;list-style:none;padding:0;margin:1rem 0}
  .steps li{counter-increment:s;padding:0.85rem 0 0.85rem 2.6rem;position:relative;border-bottom:1px solid var(--border)}
  .steps li:last-child{border-bottom:none}
  .steps li::before{content:counter(s);position:absolute;left:0;top:0.85rem;width:1.9rem;height:1.9rem;
                    background:var(--gold);color:#0a0a0a;border-radius:50%;display:flex;align-items:center;
                    justify-content:center;font-weight:700;font-family:'Playfair Display',serif}

  /* sticky contact bar */
  .sticky-cta{position:fixed;bottom:0;left:0;right:0;background:var(--panel);border-top:1px solid var(--border);
              padding:0.7rem 1rem;display:flex;gap:0.6rem;align-items:center;justify-content:space-between;z-index:60}
  .sticky-cta .meta{font-size:0.85rem;color:var(--muted)}
  .sticky-cta .meta strong{color:var(--gold);font-family:'Playfair Display',serif;font-size:1.05rem;
                            font-variant-numeric:tabular-nums;letter-spacing:0.04em;display:block}
  .sticky-cta .btn-primary{padding:0.7rem 1.1rem;font-size:0.95rem}

  /* footer */
  footer{padding:2.5rem 0 4.5rem;border-top:1px solid var(--border);margin-top:2rem;color:var(--muted);font-size:0.9rem;text-align:center}
  footer a{color:var(--muted)}
  footer a:hover{color:var(--gold)}

  @media(max-width:640px){
    .nav-links a:not(.btn-contact){display:none}
    h1{font-size:1.9rem}
    .sticky-cta .meta{display:none}
  }
  """
    for k, v in site["css_vars"].items():
        css = css.replace(f"__{k}__", v)

    # ---- structured data --------------------------------------------------
    intro_text_plain = (
        f"Etisalat {num['formatted']} — {num['category']} VIP number from {site['brand']}, "
        f"authorized Etisalat dealer in the UAE."
    )

    product_jsonld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"Etisalat {num['formatted']} ({num['category']} VIP Number)",
        "description": intro_text_plain,
        "url": page_url,
        "sku": num["msisdn"],
        "mpn": num["digits"],
        "category": f"{num['category']} VIP Mobile Number",
        "brand": {"@type": "Brand", "name": "Etisalat"},
        "offers": {
            "@type": "Offer",
            "price": str(tier["raw"]),
            "priceCurrency": "AED",
            "availability": "https://schema.org/InStock",
            "url": page_url,
            "seller": {"@type": "Organization", "name": site["brand"], "url": site["base_url"] + "/"},
        },
    }
    breadcrumb_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": site["base_url"] + "/"},
            {"@type": "ListItem", "position": 2, "name": "VIP Numbers", "item": site["base_url"] + "/numbers/"},
            {"@type": "ListItem", "position": 3, "name": f"Etisalat {num['formatted']}", "item": page_url},
        ],
    }
    faq_jsonld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }
    import json as _json
    jsonld_blocks = "\n".join(
        f'<script type="application/ld+json">{_json.dumps(b, ensure_ascii=False)}</script>'
        for b in (product_jsonld, breadcrumb_jsonld, faq_jsonld)
    )

    # ---- analytics --------------------------------------------------------
    analytics = ""
    if site["ga4"] and not site["ga4"].startswith("__"):
        analytics += (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={site["ga4"]}"></script>'
            f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}'
            f'gtag("js",new Date());gtag("config","{site["ga4"]}");</script>'
        )
    if site["fb_pixel"] and not site["fb_pixel"].startswith("__"):
        analytics += (
            "<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
            "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;"
            "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
            "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,"
            "document,'script','https://connect.facebook.net/en_US/fbevents.js');"
            f"fbq('init','{site['fb_pixel']}');fbq('track','PageView');"
            f"fbq('track','ViewContent',{{content_name:'VIP Number',content_category:'{num['category']}',"
            f"content_type:'product',content_ids:['{num['msisdn']}'],value:{tier['raw']},currency:'AED'}});"
            "</script>"
        )

    # ---- meta -------------------------------------------------------------
    title = (f"Etisalat {num['formatted']} | {num['category']} VIP Number UAE | "
             f"{tier['display']} | {site['brand']}")
    description = (
        f"Buy Etisalat number {num['formatted']} — {num['category']} VIP from {tier['display']}{tier['unit']}. "
        f"Authorized Etisalat dealer in UAE with same-day SIM delivery in Dubai, Abu Dhabi & Sharjah. "
        f"Order on WhatsApp."
    )
    keywords = (
        f"etisalat {num['digits']}, {num['formatted']}, etisalat {num['category'].lower()} number, "
        f"etisalat {info['prefix']} number, buy etisalat vip number, etisalat number uae, "
        f"etisalat number for sale, premium mobile number dubai, "
        f"{site['brand'].lower()}, vip mobile number {info['prefix']}"
    )

    og_image = f"{site['base_url']}/og-image.png"

    # ---- intro / body copy ------------------------------------------------
    intro_html = seo_intro(num, info)

    pattern_list_html = ""
    if info["patterns"]:
        pattern_list_html = (
            "<ul style='margin:0.5rem 0 0.5rem 1.2rem;color:var(--text)'>"
            + "".join(f"<li style='margin-bottom:0.3rem'>{html.escape(p.capitalize())}</li>"
                      for p in info["patterns"])
            + "</ul>"
        )

    facts_html = (
        f'<div class="facts">'
        f'  <div class="fact"><div class="k">Tier</div><div class="v">{num["category"]}</div></div>'
        f'  <div class="fact"><div class="k">Prefix</div><div class="v">{info["prefix"]}</div></div>'
        f'  <div class="fact"><div class="k">Plan from</div><div class="v">{tier["display"]}</div></div>'
        f'  <div class="fact"><div class="k">Digit-sum root</div><div class="v">{info["digit_sum_root"]}</div></div>'
        f'</div>'
    )

    def rel_html(nums, heading):
        if not nums:
            return ""
        items = "".join(
            f'<a class="rcard" href="/numbers/{slug_for(n)}/">'
            f'<span class="rnum">{html.escape(n["formatted"])}</span>'
            f'<span class="rmeta">{n["category"]} · plan from {TIER_PRICE[n["category"]]["display"]}</span>'
            f'</a>'
            for n in nums
        )
        return f'<h2>{heading}</h2><div class="related">{items}</div>'

    related_tier   = rel_html(rel_tier,   f"More {num['category']} VIP Numbers")
    related_prefix = rel_html(rel_prefix, f"More Etisalat {info['prefix']} Numbers")

    # Links UP to the category hubs this number belongs to (internal-link mesh:
    # hubs are the indexable layer, number pages feed them crawl paths).
    hub_links_html = ""
    if CURRENT_HUBS:
        _links = [f'<a href="/numbers/{h["slug"]}/">{html.escape(h["h1"])}</a>'
                  for h in CURRENT_HUBS if h["pred"](num, info)]
        if _links:
            hub_links_html = ('<section class="section"><h2>Browse by category</h2><p>'
                              + " · ".join(_links) + "</p></section>")

    faq_html = "".join(
        f'<div class="faq"><h3>{html.escape(q)}</h3><p>{html.escape(a)}</p></div>'
        for q, a in faqs
    )

    # ---- assemble ---------------------------------------------------------
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{analytics}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="keywords" content="{html.escape(keywords)}">
<meta name="theme-color" content="{site['theme_color']}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="{site['domain']}">
<link rel="canonical" href="{page_url}">

<meta property="og:type" content="product">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{page_url}">
<meta property="og:site_name" content="{site['brand']}">
<meta property="og:locale" content="en_AE">
<meta property="og:image" content="{og_image}">
<meta property="product:price:amount" content="{tier['raw']}">
<meta property="product:price:currency" content="AED">
<meta property="product:availability" content="in stock">
<meta property="product:brand" content="Etisalat">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(description)}">
<meta name="twitter:image" content="{og_image}">

<meta name="geo.region" content="AE">
<meta name="geo.placename" content="Dubai, United Arab Emirates">

<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

{jsonld_blocks}

<style>{css}</style>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Organization","name":"{site['brand']}","alternateName":"Etisalat Authorized Consultant","url":"{site['base_url']}/","logo":"{site['base_url']}/logo-square.png","image":"{site['base_url']}/logo-square.png","slogan":"Etisalat Authorized Consultant - Postpaid Plans, VIP Gold & Platinum Numbers, Free Delivery Across UAE","areaServed":"AE"}}</script>
</head>
<body>
<!-- etisalat-consultant-bar -->
<div class="etisalat-consultant-bar" style="display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;background:linear-gradient(90deg,#0D1117,#1F2630);border-bottom:1px solid #C9A962;color:#E0C58A;text-align:center;font:600 13px/1.4 'DM Sans',Arial,sans-serif;padding:7px 12px">
  <img src="/etisalat-logo.png" alt="etisalat by e& - Authorized Consultant" style="height:20px;width:auto;background:#fff;border-radius:5px;padding:2px 5px;box-sizing:content-box">
  <span>Etisalat Authorized Consultant &middot; Postpaid Plans &middot; VIP Gold &amp; Platinum Numbers &middot; Free Delivery Across UAE</span>
</div>

<nav class="nav">
  <div class="container nav-inner">
    <a class="logo" href="/">{site['brand']}</a>
    <div class="nav-links">
      <a href="/numbers/">All Numbers</a>
      <a href="/choose-number/">Browse</a>
      <a class="btn-contact" href="{wa_href}" target="_blank" rel="noopener">Contact Now</a>
    </div>
  </div>
</nav>

<div class="container">
  <nav class="crumb" aria-label="Breadcrumb">
    <a href="/">Home</a> &rsaquo; <a href="/numbers/">VIP Numbers</a> &rsaquo; Etisalat {html.escape(num['formatted'])}
  </nav>

  <header class="hero">
    <span class="tier-pill pill-{num['category']}">{num['category']} VIP Number</span>
    <h1>Etisalat Number<span class="num">{html.escape(num['formatted'])}</span></h1>
    <p class="sub">An authorized Etisalat dealer listing. {site['tagline']}.</p>
    <div class="price">{tier['display']}<small>{tier['unit']}</small></div>
    <div class="cta-row">
      <a class="btn-primary" href="{wa_href}" target="_blank" rel="noopener noreferrer" data-cta="hero_wa">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        Contact Now on WhatsApp
      </a>
      <a class="btn-secondary" href="tel:{site['wa_number']}" data-cta="call">Call {site['phone_display']}</a>
    </div>
  </header>

  {facts_html}

  <section class="section">
    <h2>About this Etisalat number</h2>
    <p>{intro_html}</p>
    {pattern_list_html}
  </section>

  <section class="section">
    <h2>What you get with the {num['category']} tier</h2>
    <p>{tier_copy}</p>
    <p>The price shown above is the entry point for this tier — final pricing for an individual VIP number depends on pattern scarcity. Confirm the live quote for {html.escape(num['formatted'])} on WhatsApp before reserving.</p>
  </section>

  <section class="section">
    <h2>How to buy {html.escape(num['formatted'])}</h2>
    <ol class="steps">
      <li><strong>Tap “Contact Now”</strong> — your WhatsApp opens with this exact number already in the message.</li>
      <li><strong>Share your Emirates ID</strong> — we reserve the number in your name with Etisalat the same day.</li>
      <li><strong>Same-day delivery</strong> — your SIM is hand-delivered across Dubai, Abu Dhabi and Sharjah, or activated on eSIM where supported.</li>
    </ol>
    <div class="cta-row" style="margin-top:1rem">
      <a class="btn-primary" href="{wa_href}" target="_blank" rel="noopener noreferrer" data-cta="midpage_wa">Contact Now on WhatsApp</a>
    </div>
  </section>

  <section class="section">
    {related_tier}
  </section>

  <section class="section">
    {related_prefix}
  </section>

  {hub_links_html}

  <section class="section">
    <h2>Frequently asked questions</h2>
    {faq_html}
  </section>

  <section class="section">
    <h2>Reserve {html.escape(num['formatted'])} now</h2>
    <p>Inventory is shared with the live Etisalat dealer system — VIP numbers can be reserved by another buyer at any time. The fastest way to lock in {html.escape(num['formatted'])} is to message us now.</p>
    <div class="cta-row">
      <a class="btn-primary" href="{wa_href}" target="_blank" rel="noopener noreferrer" data-cta="footer_wa">Contact Now on WhatsApp</a>
      <a class="btn-secondary" href="/numbers/">Browse more numbers</a>
    </div>
  </section>
</div>

<footer>
  <div class="container">
    <p>&copy; {site['brand']} — Authorized Etisalat dealer in the UAE.<br>
    <a href="/">Home</a> · <a href="/numbers/">All Numbers</a> · <a href="/choose-number/">Choose Number</a> · <a href="mailto:{site['support_email']}">{site['support_email']}</a></p>
  </div>
</footer>

<div class="sticky-cta">
  <div class="meta"><span>Etisalat · {num['category']}</span><strong>{html.escape(num['formatted'])}</strong></div>
  <a class="btn-primary" href="{wa_href}" target="_blank" rel="noopener noreferrer" data-cta="sticky_wa">Contact Now</a>
</div>

</body>
</html>"""


# ===========================================================================
# 4b. CATEGORY HUBS (/numbers/<slug>/) — quality-over-quantity indexing.
# Google declined to index 3k+ near-identical per-number pages (only ~100
# indexed). The play: ~13 genuinely differentiated, rankable category pages
# (tier / prefix / pattern), each targeting a real search query ("etisalat
# gold number", "786 number uae"), each funnelling internal links down to
# the number pages. Set CURRENT_HUBS before page_html runs so per-number
# pages link UP to their hubs (crawl mesh).
# ===========================================================================
HUB_MAX_CARDS = 240
CURRENT_HUBS = []


def _hub_membership_defs():
    """Single source of truth: hub slug, copy, and membership predicate.
    Predicates take (num, feats) where feats = analyze(num['digits'])."""
    def has(f, *words):
        return any(any(w in p for w in words) for p in f.get("patterns", []))

    defs = [
        {"slug": "gold-numbers", "label": "Gold numbers",
         "h1": "Etisalat Gold Numbers UAE",
         "intro": "Gold VIP numbers — strong patterns like repeating pairs, AABB blocks and round tails, free with the AED 500/month Etisalat postpaid plan. The most-searched VIP tier in the UAE."},
        {"slug": "silver-numbers", "label": "Silver numbers",
         "h1": "Etisalat Silver VIP Numbers UAE",
         "intro": "Entry VIP tier — memorable Etisalat numbers free with the AED 188/month postpaid plan. The fastest-moving tier in our live inventory."},
        {"slug": "platinum-numbers", "label": "Platinum numbers",
         "h1": "Etisalat Platinum Numbers UAE",
         "intro": "Ultra-VIP Etisalat numbers — five- and six-identical-digit tails and signature patterns. AED 1,000 one-time with a postpaid plan; the status tier for business owners."},
    ]
    tier_by_slug = {"gold-numbers": "Gold", "silver-numbers": "Silver", "platinum-numbers": "Platinum"}
    for d in defs:
        d["pred"] = (lambda t: lambda n, f: n["category"] == t)(tier_by_slug[d["slug"]])

    for prefix, blurb in PREFIX_INFO.items():
        defs.append({"slug": f"{prefix}-numbers", "label": f"{prefix} numbers",
                     "h1": f"Etisalat {prefix} VIP Numbers UAE",
                     "intro": blurb,
                     "pred": (lambda p: lambda n, f: f.get("prefix") == p)(prefix)})

    defs += [
        {"slug": "repeating-digit-numbers", "label": "Repeating digits",
         "h1": "Repeating-Digit Etisalat Numbers UAE",
         "intro": "Numbers ending in 3–6 identical digits (777, 8888, 99999) — the most recognisable VIP pattern in the UAE.",
         "pred": lambda n, f: has(f, "identical", "repeating", "occurrences")},
        {"slug": "mirror-numbers", "label": "Mirror numbers",
         "h1": "Mirror & Palindrome Etisalat Numbers UAE",
         "intro": "Numbers whose tails read the same forwards and backwards (52125, 7227) — subtle, memorable and rare.",
         "pred": lambda n, f: has(f, "palindrome")},
        {"slug": "round-numbers", "label": "Round numbers",
         "h1": "Round Etisalat Numbers Ending in 000",
         "intro": "Numbers ending in consecutive zeros — the classic business signature (x000, x0000).",
         "pred": lambda n, f: f.get("trailing_zeros", 0) >= 3},
        {"slug": "sequence-numbers", "label": "Sequential numbers",
         "h1": "Sequential Etisalat Numbers (1234 / 4321)",
         "intro": "Ascending and descending tails like 1234, 5678 and 4321 — clean, ordered, instantly memorable.",
         "pred": lambda n, f: has(f, "ascending", "descending")},
        {"slug": "786-numbers", "label": "786 numbers",
         "h1": "786 Numbers UAE — Lucky Etisalat Numbers",
         "intro": "Etisalat numbers containing 786 — the most requested lucky pattern in the UAE, available in Silver, Gold and Platinum tiers.",
         "pred": lambda n, f: "786" in n["digits"]},
    ]
    return defs


def build_hubs(numbers):
    """Compute hubs + members (sorted best-pattern-first). Hubs with <3 members
    are dropped — a near-empty category page is worse than none."""
    feats = {n["digits"]: analyze(n["digits"]) for n in numbers}
    hubs = []
    for d in _hub_membership_defs():
        mem = [n for n in numbers if d["pred"](n, feats[n["digits"]])]
        mem.sort(key=lambda n: feats[n["digits"]].get("score", 0), reverse=True)
        if len(mem) >= 3:
            hubs.append(dict(d, members=mem))
    return hubs


def _hub_css(css_vars):
    css = """:root{
    --bg:__bg__;--panel:__panel__;--panel2:__panel2__;--border:__border__;
    --text:__text__;--muted:__muted__;--gold:__gold__;--gold2:__gold2__;
    --silver:__silver__;--platinum:__platinum__;--green:__green__;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
  a{color:var(--gold);text-decoration:none}
  a:hover{text-decoration:underline}
  .container{max-width:1100px;margin:0 auto;padding:0 1.25rem}
  .nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--border);padding:0.9rem 0;z-index:50}
  .nav-inner{display:flex;justify-content:space-between;align-items:center}
  .logo{font-family:'Playfair Display',serif;font-weight:700;font-size:1.35rem;color:var(--gold)}
  .nav-links{display:flex;gap:1.25rem;align-items:center}
  .nav-links a{color:var(--text);font-weight:500;font-size:0.95rem}
  .btn-contact{background:var(--green);color:#fff !important;padding:0.55rem 1.1rem;border-radius:999px;font-weight:600;font-size:0.9rem}
  .hero{padding:2.5rem 0 1.5rem;text-align:center}
  h1{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3rem);font-weight:700;margin-bottom:0.6rem}
  .sub{color:var(--muted);max-width:680px;margin:0 auto 1.5rem;font-size:1.05rem}
  .section{padding:2rem 0;border-top:1px solid var(--border)}
  .section h2{font-family:'Playfair Display',serif;font-size:1.5rem;margin-bottom:1rem}
  .related{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:0.75rem}
  .rcard{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:1rem;display:flex;flex-direction:column;gap:0.4rem;transition:border-color .15s}
  .rcard:hover{border-color:var(--gold);text-decoration:none}
  .rcard .rnum{font-family:'Playfair Display',serif;font-size:1.2rem;color:var(--gold);font-variant-numeric:tabular-nums;letter-spacing:0.04em}
  .rcard .rmeta{font-size:0.82rem;color:var(--muted)}
  footer{padding:3rem 0;border-top:1px solid var(--border);margin-top:2rem;color:var(--muted);font-size:0.9rem;text-align:center}
  footer a{color:var(--muted)}
  """
    for k, v in css_vars.items():
        css = css.replace(f"__{k}__", v)
    return css


def _hub_browse_section(hubs, current_slug=None):
    """'Browse by category' card grid used on the main hub + each category hub."""
    if not hubs:
        return ""
    cards = "".join(
        f'<a class="rcard" href="/numbers/{h["slug"]}/">'
        f'<span class="rnum">{html.escape(h["label"])}</span>'
        f'<span class="rmeta">{len(h["members"])} available</span></a>'
        for h in hubs if h["slug"] != current_slug
    )
    return f'<section class="section"><h2>Browse by category</h2><div class="related">{cards}</div></section>'


def hub_page_html(site, hub, hubs):
    """One rankable category landing page: unique intro, best-pattern-first
    card grid (capped), CollectionPage/ItemList JSON-LD, hub cross-links."""
    members = hub["members"]
    shown = members[:HUB_MAX_CARDS]
    more = len(members) - len(shown)
    hub_url = f"{site['base_url']}/numbers/{hub['slug']}/"
    title = f"{hub['h1']} — {len(members)} Available | {site['brand']}"
    description = (f"{hub['intro']} {len(members)} available now from {site['brand']}, "
                   f"authorized Etisalat dealer — same-day SIM delivery across the UAE.")

    cards = "".join(
        f'<a class="rcard" href="/numbers/{slug_for(n)}/">'
        f'<span class="rnum">{html.escape(n["formatted"])}</span>'
        f'<span class="rmeta">{n["category"]} · plan from {TIER_PRICE[n["category"]]["display"]}</span>'
        f'</a>'
        for n in shown
    )
    more_html = (f'<p style="margin-top:1rem;color:var(--muted)">+ {more} more in live inventory — '
                 f'<a href="/choose-number/">browse the full picker</a>.</p>') if more > 0 else ""

    item_list = ",".join(
        f'{{"@type":"ListItem","position":{i + 1},"url":"{url_for(site, n)}","name":"{n["formatted"]}"}}'
        for i, n in enumerate(shown[:25])
    )
    jsonld = (f'{{"@context":"https://schema.org","@type":"CollectionPage","name":"{html.escape(hub["h1"])}",'
              f'"url":"{hub_url}","isPartOf":{{"@type":"WebSite","name":"{site["brand"]}","url":"{site["base_url"]}/"}},'
              f'"mainEntity":{{"@type":"ItemList","numberOfItems":{len(members)},"itemListElement":[{item_list}]}}}}')

    wa_msg = f"Hi, I'm interested in {hub['label']} from {site['domain']}"
    wa_href = f"https://wa.me/{site['wa_number']}?text={urllib.parse.quote(wa_msg)}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="{site['theme_color']}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{hub_url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{hub_url}">
<link rel="icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>{_hub_css(site['css_vars'])}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<nav class="nav">
  <div class="container nav-inner">
    <a class="logo" href="/">{site['brand']}</a>
    <div class="nav-links">
      <a href="/numbers/">All Numbers</a>
      <a href="/choose-number/">Browse</a>
      <a class="btn-contact" href="{wa_href}" target="_blank" rel="noopener">Contact Now</a>
    </div>
  </div>
</nav>

<header class="container hero">
  <h1>{html.escape(hub['h1'])}</h1>
  <p class="sub">{html.escape(hub['intro'])} Live inventory: {len(members)} available today.</p>
</header>

<main class="container">
  <section class="section">
    <div class="related">{cards}</div>
    {more_html}
  </section>
  {_hub_browse_section(hubs, current_slug=hub['slug'])}
</main>

<footer>
  <div class="container">
    <p>&copy; {site['brand']} — Authorized Etisalat dealer in the UAE.<br>
    <a href="/">Home</a> · <a href="/numbers/">All Numbers</a> · <a href="/choose-number/">Choose Number</a></p>
  </div>
</footer>

</body>
</html>"""


# ===========================================================================
# 5. HUB INDEX (/numbers/)
# ===========================================================================
def hub_index_html(site, numbers, hubs=None):
    css_vars = site["css_vars"]
    by_tier = defaultdict(list)
    for n in numbers:
        by_tier[n["category"]].append(n)
    tier_order = ["Platinum", "Gold", "Silver"]

    def render_tier_block(tier_name):
        nums = by_tier.get(tier_name, [])
        if not nums:
            return ""
        cards = "".join(
            f'<a class="rcard" href="/numbers/{slug_for(n)}/">'
            f'<span class="rnum">{html.escape(n["formatted"])}</span>'
            f'<span class="rmeta">{n["category"]} · plan from {TIER_PRICE[n["category"]]["display"]}</span>'
            f'</a>'
            for n in nums
        )
        return f"""
        <section class="section">
          <h2>{tier_name} VIP Numbers <small style="font-weight:400;color:var(--muted);font-size:0.95rem">({len(nums)} available)</small></h2>
          <div class="related">{cards}</div>
        </section>"""

    title = f"All Etisalat VIP Numbers UAE | {len(numbers)} Available | {site['brand']}"
    description = (
        f"Browse all {len(numbers)} available Etisalat VIP numbers in the UAE — "
        f"Silver, Gold and Platinum tiers from {site['brand']}, authorized Etisalat dealer. "
        f"Same-day SIM delivery in Dubai, Abu Dhabi and Sharjah."
    )

    # NOTE: was `""" % css_vars` — a no-op with a dict and no %()s placeholders,
    # which shipped literal __bg__ vars to production. _hub_css does the replace.
    css = _hub_css(css_vars)

    wa_msg = f"Hi, I'd like to browse available Etisalat VIP numbers from {site['domain']}"
    wa_href = f"https://wa.me/{site['wa_number']}?text={urllib.parse.quote(wa_msg)}"

    body_blocks = "".join(render_tier_block(t) for t in tier_order)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="{site['theme_color']}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{site['base_url']}/numbers/">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{site['base_url']}/numbers/">
<link rel="icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Organization","name":"{site['brand']}","alternateName":"Etisalat Authorized Consultant","url":"{site['base_url']}/","logo":"{site['base_url']}/logo-square.png","image":"{site['base_url']}/logo-square.png","slogan":"Etisalat Authorized Consultant - Postpaid Plans, VIP Gold & Platinum Numbers, Free Delivery Across UAE","areaServed":"AE"}}</script>
</head>
<body>
<!-- etisalat-consultant-bar -->
<div class="etisalat-consultant-bar" style="display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;background:linear-gradient(90deg,#0D1117,#1F2630);border-bottom:1px solid #C9A962;color:#E0C58A;text-align:center;font:600 13px/1.4 'DM Sans',Arial,sans-serif;padding:7px 12px">
  <img src="/etisalat-logo.png" alt="etisalat by e& - Authorized Consultant" style="height:20px;width:auto;background:#fff;border-radius:5px;padding:2px 5px;box-sizing:content-box">
  <span>Etisalat Authorized Consultant &middot; Postpaid Plans &middot; VIP Gold &amp; Platinum Numbers &middot; Free Delivery Across UAE</span>
</div>

<nav class="nav">
  <div class="container nav-inner">
    <a class="logo" href="/">{site['brand']}</a>
    <div class="nav-links">
      <a href="/choose-number/">Browse</a>
      <a class="btn-contact" href="{wa_href}" target="_blank" rel="noopener">Contact Now</a>
    </div>
  </div>
</nav>

<header class="container hero">
  <h1>All Etisalat VIP Numbers</h1>
  <p class="sub">Live inventory of every available Etisalat VIP number from {site['brand']} — sorted by tier. Each number has its own page with pattern detail, pricing and an instant WhatsApp inquiry button.</p>
</header>

<main class="container">
  {_hub_browse_section(hubs)}
  {body_blocks}
</main>

<footer>
  <div class="container">
    <p>&copy; {site['brand']} — Authorized Etisalat dealer in the UAE.<br>
    <a href="/">Home</a> · <a href="/choose-number/">Choose Number</a></p>
  </div>
</footer>

</body>
</html>"""


# ===========================================================================
# 6. SITEMAP
# ===========================================================================
def write_sitemap_numbers(site, numbers, hubs=None):
    """Write /sitemap-numbers.xml with one entry per number page + the hub
    + the category hubs. Then write /sitemap-index.xml that points to both the
    original sitemap.xml and sitemap-numbers.xml, so GSC sees a single
    submission point."""
    proj = site["project_dir"]
    base = site["base_url"]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.append(f'  <url><loc>{base}/numbers/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>')
    for h in (hubs or []):
        lines.append(f'  <url><loc>{base}/numbers/{h["slug"]}/</loc><changefreq>daily</changefreq><priority>0.85</priority></url>')
    for n in numbers:
        lines.append(f'  <url><loc>{base}/numbers/{slug_for(n)}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    lines.append('</urlset>')
    out = "\n".join(lines)
    path = os.path.join(proj, "sitemap-numbers.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"  wrote {path}  ({len(numbers)+1} URLs)")

    # sitemap-index.xml — points to existing sitemap.xml AND sitemap-numbers.xml
    idx_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                 f'  <sitemap><loc>{base}/sitemap.xml</loc></sitemap>',
                 f'  <sitemap><loc>{base}/sitemap-numbers.xml</loc></sitemap>',
                 '</sitemapindex>']
    idx_path = os.path.join(proj, "sitemap-index.xml")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write("\n".join(idx_lines))
    print(f"  wrote {idx_path}")


# ===========================================================================
# 7. ORCHESTRATION
# ===========================================================================
def generate_for_site(site, numbers):
    global CURRENT_HUBS
    print(f"\n=== {site['label']} -> {len(numbers)} numbers ===")
    out_root = os.path.join(site["project_dir"], "numbers")
    os.makedirs(out_root, exist_ok=True)

    # Category hubs FIRST so per-number pages can link up to them.
    hubs = build_hubs(numbers)
    CURRENT_HUBS = hubs

    # Per-number pages
    written = 0
    for num in numbers:
        slug = slug_for(num)
        out_dir = os.path.join(out_root, slug)
        os.makedirs(out_dir, exist_ok=True)
        html_out = page_html(site, num, numbers)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)
        written += 1
        if written % 200 == 0:
            print(f"  ...{written} pages written")

    # Category hub pages
    for h in hubs:
        hd = os.path.join(out_root, h["slug"])
        os.makedirs(hd, exist_ok=True)
        with open(os.path.join(hd, "index.html"), "w", encoding="utf-8") as f:
            f.write(hub_page_html(site, h, hubs))
    print(f"  wrote {len(hubs)} category hubs: " + ", ".join(h["slug"] for h in hubs))

    # Hub index
    hub = hub_index_html(site, numbers, hubs)
    with open(os.path.join(out_root, "index.html"), "w", encoding="utf-8") as f:
        f.write(hub)
    print(f"  wrote /numbers/index.html (hub)")

    # Sitemaps
    write_sitemap_numbers(site, numbers, hubs)
    print(f"  done: {written} per-number pages + {len(hubs)} hubs + sitemap-numbers.xml")


def main():
    targets = sys.argv[1:] or list(SITES.keys())
    print(f"Loading numbers from {len(SHEETS)} sheets...")
    numbers = load_all_numbers()
    print(f"  -> {len(numbers)} Available numbers across all tiers")
    by_cat = Counter(n["category"] for n in numbers)
    for k, v in by_cat.most_common():
        print(f"     {k}: {v}")
    if not numbers:
        print("No numbers fetched — aborting.")
        return 1

    for key in targets:
        site = SITES.get(key)
        if not site:
            print(f"Unknown site key '{key}'  — valid: {list(SITES)}")
            continue
        generate_for_site(site, numbers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
