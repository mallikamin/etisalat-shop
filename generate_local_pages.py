# -*- coding: utf-8 -*-
"""
generate_local_pages.py, city + area local SEO pages for goldennummbers.com (2026-06-06)

Generates 21 pages, three kinds:
  numbers  → 5 emirate pages missing from the /dubai/ /abu-dhabi/ /sharjah/ family
  internet → 8 home-internet city pages (5.5G Home Wireless, local angle)
  area     → 8 Dubai-area DUAL pages (numbers + internet on one page, avoids 2x thin pages)

Single source of truth: edit LOCATIONS below, rerun. Each location carries UNIQUE
intro copy, area/landmark lists and FAQ wording (anti-thin-page rule per the May
number-pages lesson). Visible FAQ and FAQPage JSON-LD emit from the same data.

CTAs (Malik 2026-06-06):
  numbers  → "Talk to a LIVE Etisalat Specialist Agent Now" (WA 8087) + "Browse Numbers" (/choose-number/)
  internet → "Talk to a LIVE Etisalat Specialist Agent Now" (WA 8087) + "Explore Home Internet Plans" (/home-wireless/)
  area     → both pairs, one per product section
"""
import json
import re
from pathlib import Path

ROOT = Path(r"C:\Users\Malik\desktop\etisalat-shop")
BASE = "https://goldennummbers.com"
WA_NUM = "https://wa.me/971569028087?text=Hi%2C%20I%20want%20to%20reserve%20a%20postpaid%20number%20from%20goldennummbers.com"
WA_HW = "https://wa.me/971569028087?text=Hi%2C%20I%20want%20to%20order%20Etisalat%20Home%20Wireless%20from%20goldennummbers.com"
WA_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'

# (kind, slug, name, geo_region, lat, lng, areas[], intro, local_hook, cross_slug)
# intro = unique opening paragraph; local_hook = one extra location-flavored sentence used in FAQ/delivery copy
LOCATIONS = [
    # ---- numbers: missing emirates ----
    dict(kind="numbers", slug="ajman", name="Ajman", region="AE-AJ", lat="25.4052", lng="55.5136",
         areas=["Al Nuaimiya", "Al Rashidiya", "Ajman Corniche", "Al Jurf", "Al Mowaihat", "Emirates City", "Al Rawda", "Garden City", "Al Zahra", "Musherief"],
         intro="Ajman's business community runs on referrals and repeat customers, and a memorable Etisalat number is the cheapest marketing asset a Nuaimiya shop or Al Jurf trader can own. We deliver VIP SIMs across Ajman the same day, free.",
         hook="From Al Nuaimiya towers to the industrial areas of Al Jurf, delivery typically lands the same day you confirm on WhatsApp."),
    dict(kind="numbers", slug="al-ain", name="Al Ain", region="AE-AZ", lat="24.2075", lng="55.7447",
         areas=["Al Jimi", "Al Muwaiji", "Town Centre", "Al Yahar", "Hili", "Al Maqam", "Zakher", "Al Foah", "Al Khabisi", "Falaj Hazza"],
         intro="The Garden City prefers numbers that last a lifetime, family numbers, majlis numbers, business numbers passed between generations. We bring Etisalat Gold, Silver and Platinum patterns to Al Ain with free delivery to your door.",
         hook="We deliver across Al Ain, Al Jimi, Hili, Zakher, Al Yahar and the Town Centre, usually within the same day."),
    dict(kind="numbers", slug="ras-al-khaimah", name="Ras Al Khaimah", region="AE-RK", lat="25.7895", lng="55.9432",
         areas=["Al Nakheel", "Al Hamra Village", "Mina Al Arab", "Al Dhait", "Khuzam", "Al Rams", "Julfar", "Al Qusaidat", "Seih Al Uraibi"],
         intro="From Al Hamra Village residences to Al Nakheel's trading streets, a golden Etisalat number gets your call answered in Ras Al Khaimah. Browse live Silver, Gold and Platinum inventory and have the SIM delivered free.",
         hook="RAK deliveries cover Al Nakheel, Al Hamra, Mina Al Arab, Al Dhait and beyond, confirmed on WhatsApp before dispatch."),
    dict(kind="numbers", slug="fujairah", name="Fujairah", region="AE-FU", lat="25.1288", lng="56.3265",
         areas=["Fujairah City Centre", "Dibba Al-Fujairah", "Al Faseel", "Sakamkam", "Al Hala", "Mirbah", "Qidfa", "Al Aqah"],
         intro="On the east coast, business moves through the port, the free zone and a phone number people remember. We deliver Etisalat VIP numbers across Fujairah, from the City Centre to Dibba, with the postpaid plan activated and ready.",
         hook="East-coast delivery reaches Fujairah City, Al Faseel, Sakamkam, Dibba and Al Aqah, timing confirmed on WhatsApp."),
    dict(kind="numbers", slug="umm-al-quwain", name="Umm Al Quwain", region="AE-UQ", lat="25.5647", lng="55.5534",
         areas=["Al Salamah", "Old Town", "Al Raas", "Al Haditha", "Emirates Modern Industrial Area", "Falaj Al Mualla", "Al Humrah"],
         intro="Umm Al Quwain keeps it simple: one good number, kept for years. Choose a Silver, Gold or Platinum Etisalat pattern from live inventory and we deliver the SIM free to Al Salamah, Old Town, Al Raas or anywhere in the emirate.",
         hook="UAQ is fully covered, Al Salamah, Old Town, Al Raas, the industrial area and Falaj Al Mualla."),

    # ---- internet: 8 city pages ----
    dict(kind="internet", slug="home-internet-dubai", name="Dubai", region="AE-DU", lat="25.2048", lng="55.2708",
         areas=["Dubai Marina", "JBR", "Downtown Dubai", "Business Bay", "DIFC", "Palm Jumeirah", "JLT", "Deira", "Bur Dubai", "Al Barsha", "JVC", "Dubai Hills", "Silicon Oasis", "International City", "Mirdif", "Al Quoz"],
         intro="New apartment in Marina? Villa in Dubai Hills still waiting on fiber? 5.5G Home Wireless gets any Dubai home online within 24 hours, the router is delivered free, you plug it in, and the WiFi is live. No technician booking, no cabling through a rented apartment.",
         hook="Dubai deliveries run daily across Marina, Downtown, Deira, Bur Dubai, JVC, Dubai Hills and every other district.",
         cross="dubai"),
    dict(kind="internet", slug="home-internet-abu-dhabi", name="Abu Dhabi", region="AE-AZ", lat="24.4539", lng="54.3773",
         areas=["Al Reem Island", "Khalifa City", "Al Khalidiyah", "Corniche", "Mussafah", "Yas Island", "Saadiyat Island", "Al Nahyan", "Mohammed Bin Zayed City", "Al Wahda", "Madinat Zayed", "Al Raha"],
         intro="From Al Reem towers to Khalifa City villas, Abu Dhabi homes don't need to wait for an installation slot. 5.5G Home Wireless arrives at your door within 24 hours, free, plug the router in and your unlimited home WiFi is running the same evening.",
         hook="We deliver across the island and the mainland, Reem, Khalidiyah, Mussafah, Khalifa City, MBZ City, Yas and Saadiyat.",
         cross="abu-dhabi"),
    dict(kind="internet", slug="home-internet-sharjah", name="Sharjah", region="AE-SH", lat="25.3463", lng="55.4209",
         areas=["Al Nahda", "Al Majaz", "Al Khan", "Al Taawun", "Muwaileh", "Al Qasimia", "Abu Shagara", "Rolla", "Al Yarmook", "University City"],
         intro="Sharjah families stream, study and work from home more than anywhere in the UAE, and share buildings where fiber appointments take days. 5.5G Home Wireless skips the queue: free router delivery to Al Nahda, Al Majaz or Muwaileh within 24 hours, unlimited data from day one.",
         hook="Al Nahda, Al Majaz, Al Khan, Al Taawun, Muwaileh, Rolla and University City are all on the daily delivery routes.",
         cross="sharjah"),
    dict(kind="internet", slug="home-internet-ajman", name="Ajman", region="AE-AJ", lat="25.4052", lng="55.5136",
         areas=["Al Nuaimiya", "Al Rashidiya", "Ajman Corniche", "Al Jurf", "Emirates City", "Al Mowaihat", "Garden City", "Al Rawda"],
         intro="Ajman rents are the best value in the UAE, your internet should be too. 5.5G Home Wireless gives Nuaimiya and Corniche apartments unlimited home WiFi at AED 206/month with no upfront payment and a free router delivered within 24 hours.",
         hook="Nuaimiya, Rashidiya, the Corniche towers, Al Jurf and Emirates City all get free 24-hour delivery.",
         cross="ajman"),
    dict(kind="internet", slug="home-internet-al-ain", name="Al Ain", region="AE-AZ", lat="24.2075", lng="55.7447",
         areas=["Al Jimi", "Al Muwaiji", "Town Centre", "Hili", "Al Yahar", "Al Maqam", "Zakher", "Falaj Hazza"],
         intro="Al Ain's villas and farms sit exactly where fixed-line rollout is slowest, and where wireless internet makes the most sense. The 5.5G router works the moment it's plugged in, anywhere the Etisalat network reaches, with unlimited local data.",
         hook="Villas in Zakher, Al Yahar, Hili and Al Jimi are exactly the homes 5.5G was made for, no trenching, no cabling.",
         cross="al-ain"),
    dict(kind="internet", slug="home-internet-ras-al-khaimah", name="Ras Al Khaimah", region="AE-RK", lat="25.7895", lng="55.9432",
         areas=["Al Nakheel", "Al Hamra Village", "Mina Al Arab", "Al Dhait", "Khuzam", "Al Rams", "Julfar"],
         intro="Whether it's an Al Hamra holiday home or a family villa in Al Dhait, RAK homes get online faster on 5.5G than on any installation appointment. Free router, free 24-hour delivery, unlimited data, and the router moves with you if you relocate.",
         hook="Al Hamra Village, Mina Al Arab, Al Nakheel and Al Dhait are covered by free 24-hour delivery.",
         cross="ras-al-khaimah"),
    dict(kind="internet", slug="home-internet-fujairah", name="Fujairah", region="AE-FU", lat="25.1288", lng="56.3265",
         areas=["Fujairah City Centre", "Dibba Al-Fujairah", "Al Faseel", "Sakamkam", "Mirbah", "Al Aqah"],
         intro="East-coast buildings wait longest for fixed-line internet, Fujairah is where plug-and-play 5.5G earns its keep. The router is delivered free from the City Centre to Dibba, and your unlimited home WiFi is live the same day it arrives.",
         hook="Fujairah City, Al Faseel, Sakamkam, Mirbah, Al Aqah and Dibba are all reachable within the 24-hour window.",
         cross="fujairah"),
    dict(kind="internet", slug="home-internet-umm-al-quwain", name="Umm Al Quwain", region="AE-UQ", lat="25.5647", lng="55.5534",
         areas=["Al Salamah", "Old Town", "Al Raas", "Al Haditha", "Falaj Al Mualla"],
         intro="UAQ homes shouldn't pay Dubai prices for internet, or wait Dubai queues for installation. 5.5G Home Wireless brings unlimited home WiFi to Al Salamah and Old Town at AED 206/month, with the router delivered free within 24 hours.",
         hook="Al Salamah, Old Town, Al Raas and Falaj Al Mualla, all covered, no installation visit needed.",
         cross="umm-al-quwain"),

    # ---- area: 8 Dubai dual-product pages ----
    dict(kind="area", slug="dubai-marina", name="Dubai Marina", region="AE-DU", lat="25.0805", lng="55.1403",
         areas=["Marina Walk", "Marina Promenade", "Marina Gate", "Damac Heights", "Princess Tower", "Marina Mall area", "Al Sufouh edge"],
         intro="Marina moves fast: new tenants every season, businesses run from tower apartments, and nobody waits a week for an installation appointment. We deliver both, VIP Etisalat numbers for the personal brand, and 5.5G home internet for the apartment, to any Marina tower, free.",
         hook="Tower deliveries across Marina Walk, Marina Gate, Princess Tower and the Promenade usually land the same day."),
    dict(kind="area", slug="deira", name="Deira", region="AE-DU", lat="25.2716", lng="55.3082",
         areas=["Gold Souk", "Al Rigga", "Naif", "Port Saeed", "Al Muraqqabat", "Abu Hail", "Hor Al Anz", "Al Baraha"],
         intro="Deira is where UAE trading started, and where a golden number still closes deals. From Gold Souk wholesalers to Al Rigga offices, we deliver memorable Etisalat numbers and plug-and-play 5.5G home internet across Deira, same day, free.",
         hook="Gold Souk, Naif, Al Rigga, Al Muraqqabat and Hor Al Anz are our home turf, many of our partner shops are here."),
    dict(kind="area", slug="business-bay", name="Business Bay", region="AE-DU", lat="25.1850", lng="55.2650",
         areas=["Bay Square", "Executive Towers", "Marasi Drive", "Churchill Towers", "Al Abraj Street", "Canal-side towers"],
         intro="In Business Bay the phone number on your card is part of the pitch. Pair a Gold or Platinum Etisalat number with your company line, and put 5.5G wireless internet in the office or apartment, both delivered free to any Bay tower.",
         hook="Bay Square, Executive Towers and the Marasi Drive towers get same-day delivery, order before evening on WhatsApp."),
    dict(kind="area", slug="jbr", name="JBR", region="AE-DU", lat="25.0750", lng="55.1330",
         areas=["The Walk", "The Beach", "Bahar", "Rimal", "Murjan", "Shams", "Amwaj", "Sadaf"],
         intro="JBR apartments turn over fast, holiday lets, new leases, short stays. 5.5G home internet is made for that: plug in, online, and it moves out with you. Add a memorable Etisalat number and you're fully set up the day you get the keys.",
         hook="All six JBR clusters, Bahar, Rimal, Murjan, Shams, Amwaj, Sadaf, plus The Walk and The Beach are covered daily."),
    dict(kind="area", slug="downtown-dubai", name="Downtown Dubai", region="AE-DU", lat="25.1972", lng="55.2744",
         areas=["Burj Khalifa district", "Dubai Mall area", "Old Town", "Opera District", "Boulevard Central", "South Ridge", "The Residences"],
         intro="A Downtown address deserves a number that matches. Platinum and Gold Etisalat patterns suit the Burj Khalifa business card, and 5.5G wireless internet has your Boulevard apartment online the day you move in, no installation visit through concierge.",
         hook="Boulevard, Old Town, Opera District and South Ridge deliveries clear building security with a simple WhatsApp confirmation."),
    dict(kind="area", slug="bur-dubai", name="Bur Dubai", region="AE-DU", lat="25.2532", lng="55.2972",
         areas=["Meena Bazaar", "Al Fahidi", "Al Mankhool", "Golden Sands", "Oud Metha", "Al Raffa", "Al Hamriya"],
         intro="Bur Dubai's trading families have kept the same numbers for decades, that's the power of a memorable pattern. We stock Silver, Gold and Platinum Etisalat numbers and deliver them (plus 5.5G home internet) across Meena Bazaar, Mankhool and Golden Sands, free.",
         hook="Meena Bazaar, Al Fahidi, Mankhool, Golden Sands and Oud Metha, same-day delivery on WhatsApp confirmation."),
    dict(kind="area", slug="al-barsha", name="Al Barsha", region="AE-DU", lat="25.1107", lng="55.2030",
         areas=["Al Barsha 1", "Al Barsha 2", "Al Barsha 3", "Barsha Heights", "Mall of the Emirates area", "Al Barsha South"],
         intro="Between Mall of the Emirates traffic and Barsha Heights offices, this is one of Dubai's busiest residential-business mixes. We deliver VIP Etisalat numbers for the business and 5.5G wireless internet for the villa or apartment, free, within 24 hours.",
         hook="Barsha 1-3, Barsha South and Barsha Heights (Tecom) are on daily routes; villas and towers both covered."),
    dict(kind="area", slug="jlt", name="JLT", region="AE-DU", lat="25.0700", lng="55.1400",
         areas=["Cluster A-Z towers", "JLT Park area", "DMCC Free Zone", "Almas Tower area", "Lake Level shops"],
         intro="JLT runs on small business, DMCC licences, tower offices, founders running companies from Cluster D. A Gold Etisalat number makes the company feel established; 5.5G wireless internet gets the office (or apartment) online without waiting on building management for cabling.",
         hook="All JLT clusters and DMCC towers covered, delivery to tower reception or your door, free, within 24 hours."),
]

# ---------- shared page chrome ----------

HEAD_TRACKING = """<!-- Google tag (gtag.js), GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-G34631QW03"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-G34631QW03');
</script>
"""

FB_PIXEL = """<!-- Facebook Pixel -->
<script>
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '1456083435966506');
  fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=1456083435966506&ev=PageView&noscript=1"/></noscript>
"""

CSS = """*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0D1117;--surface:#161B22;--surface-border:#21262D;--gold:#C9A962;--gold-light:#E8D5A3;--text:#F5F5F0;--text-muted:rgba(245,245,240,0.65);--font-heading:'Playfair Display',Georgia,serif;--font-body:'DM Sans',-apple-system,sans-serif}
html{scroll-behavior:smooth}
body{font-family:var(--font-body);background:var(--bg);color:var(--text);line-height:1.6;overflow-x:hidden}
a{color:inherit;text-decoration:none}
.container{max-width:1100px;margin:0 auto;padding:0 1.5rem}
nav{background:rgba(13,17,23,0.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--surface-border);padding:1rem 0;position:sticky;top:0;z-index:100}
nav .container{display:flex;align-items:center;justify-content:space-between}
.nav-logo{font-family:var(--font-heading);font-size:1.3rem;color:var(--gold)}
.nav-links{display:flex;gap:1.5rem;flex-wrap:wrap}
.nav-links a{color:var(--text-muted);font-size:0.9rem;transition:color 0.2s}
.nav-links a:hover{color:var(--gold)}
.hero{padding:4rem 0 3.5rem;text-align:center;border-bottom:1px solid var(--surface-border)}
.hero h1{font-family:var(--font-heading);font-size:2.4rem;margin-bottom:1rem;line-height:1.2}
.hero h1 span{background:linear-gradient(135deg,var(--gold),var(--gold-light));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero p{color:var(--text-muted);font-size:1.05rem;max-width:660px;margin:0 auto 2rem}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.85rem 1.8rem;border-radius:8px;font-size:0.95rem;font-weight:600;transition:all 0.3s;cursor:pointer;border:none}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--gold-light));color:var(--bg)}
.btn-gold:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(201,169,98,0.3)}
.btn-wa-green{background:#25D366;color:#fff}
.btn-wa-green:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(37,211,102,0.3)}
.btn-outline{border:1.5px solid var(--gold);color:var(--gold);background:transparent}
.btn-outline:hover{background:rgba(201,169,98,0.12)}
.trust-strip{padding:1.5rem 0;background:var(--surface);border-bottom:1px solid var(--surface-border)}
.trust-strip .container{display:flex;justify-content:center;align-items:center;gap:2rem;flex-wrap:wrap}
.trust-item{display:flex;align-items:center;gap:0.5rem;color:var(--text-muted);font-size:0.85rem}
section{padding:3.5rem 0}
.section-heading{text-align:center;margin-bottom:2.25rem}
.section-heading h2{font-family:var(--font-heading);font-size:1.7rem;margin-bottom:0.5rem}
.section-heading p{color:var(--text-muted);font-size:0.95rem}
.tier-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.5rem;max-width:980px;margin:0 auto}
.tier-card{background:var(--surface);border:1px solid var(--surface-border);border-radius:12px;padding:1.5rem;text-align:center;transition:all 0.3s}
.tier-card:hover{border-color:var(--gold)}
.tier-card h3{font-family:var(--font-heading);margin-bottom:0.35rem}
.tier-card .tc-price{font-size:1.5rem;font-weight:700;color:var(--gold)}
.tier-card .tc-price small{font-size:0.78rem;color:var(--text-muted);font-weight:400}
.tier-card p{color:var(--text-muted);font-size:0.88rem;margin:0.6rem 0 1rem}
.areas{display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;max-width:820px;margin:0 auto}
.area-tag{background:var(--surface);border:1px solid var(--surface-border);padding:0.4rem 1rem;border-radius:20px;font-size:0.85rem;color:var(--text-muted)}
.check-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:0.75rem;max-width:760px;margin:0 auto 1.5rem}
.check-grid div{background:var(--surface);border:1px solid rgba(201,169,98,0.35);border-radius:10px;padding:0.8rem 1rem;color:var(--text);font-size:0.9rem;font-weight:600}
.faq-item{background:var(--surface);border:1px solid var(--surface-border);border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1rem}
.faq-item h3{font-size:1rem;margin-bottom:0.5rem;color:var(--text)}
.faq-item p{color:var(--text-muted);font-size:0.9rem;line-height:1.6}
.cta-section{text-align:center;padding:3.5rem 0;background:var(--surface);border-top:1px solid var(--surface-border)}
footer{padding:2rem 0;border-top:1px solid var(--surface-border);text-align:center;color:var(--text-muted);font-size:0.85rem}
footer a{color:var(--text-muted);transition:color 0.2s}
footer a:hover{color:var(--gold)}
.footer-links{display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;margin-bottom:1rem}
.gn-cta-sticky{position:fixed;z-index:9990;display:flex}
.gn-cta-sticky a{display:flex;align-items:center;justify-content:center;gap:7px;font-weight:700;text-decoration:none;text-align:center}
.gn-cta-sticky .gn-cta-wa{background:#25D366;color:#fff}
.gn-cta-sticky .gn-cta-browse{background:#C9A962;color:#0D1117}
.gn-cta-sticky svg{width:18px;height:18px;flex:none}
@media(max-width:1199px){
  .gn-cta-sticky{left:0;right:0;bottom:0;gap:8px;padding:8px 10px calc(8px + env(safe-area-inset-bottom));background:rgba(13,17,23,.96);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-top:1px solid rgba(201,169,98,.35)}
  .gn-cta-sticky a{flex:1;padding:11px 6px;border-radius:9px;font-size:12.5px;line-height:1.25}
  body{padding-bottom:80px}
}
@media(min-width:1200px){
  .gn-cta-sticky{flex-direction:column;gap:10px;right:18px;top:50%;transform:translateY(-50%);max-width:225px}
  .gn-cta-sticky a{padding:12px 18px;border-radius:999px;font-size:13.5px;box-shadow:0 6px 18px rgba(0,0,0,.4)}
}
@media(max-width:768px){.hero h1{font-size:1.7rem}.nav-links{gap:0.8rem}.trust-strip .container{gap:1rem}}"""

EC_BAR = """<!-- ec-bar -->
<style id="ec-bar-css">
.etisalat-consultant-bar{position:fixed;top:0;left:0;right:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;background:linear-gradient(90deg,#0D1117,#1F2630);border-bottom:1px solid #C9A962;color:#E0C58A;text-align:center;font:600 13px/1.35 'DM Sans',Arial,sans-serif;padding:6px 14px}
.etisalat-consultant-bar img{flex:none;height:22px;width:auto;background:#fff;border-radius:5px;padding:3px 6px;box-sizing:content-box}
.navbar,body>nav,.nav{top:var(--ec-bar-h,0)!important}
@media(max-width:600px){.etisalat-consultant-bar{font-size:11px;line-height:1.3;gap:7px;padding:5px 10px}.etisalat-consultant-bar img{height:17px;padding:2px 5px}}
</style>
<div class="etisalat-consultant-bar">
  <img src="/etisalat-logo.png" alt="etisalat by e& - Authorized Consultant">
  <span>Etisalat Authorized Consultant &middot; Postpaid Plans &middot; VIP Gold &amp; Platinum Numbers &middot; Free Delivery Across UAE</span>
</div>
<script id="ec-bar-js">(function(){function f(){var b=document.querySelector(".etisalat-consultant-bar");if(!b)return;var h=b.offsetHeight;document.documentElement.style.setProperty('--ec-bar-h',h+'px');document.body.style.paddingTop=h+'px';}f();window.addEventListener('load',f);window.addEventListener('resize',f);if(document.fonts&&document.fonts.ready){document.fonts.ready.then(f);}setTimeout(f,400);})();</script>
<!-- /ec-bar -->
"""


def nav_html():
    return """<nav>
  <div class="container">
    <a href="/" class="nav-logo">goldennummbers.com</a>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/choose-number/">VIP Numbers</a>
      <a href="/home-wireless/">Home Internet</a>
      <a href="/blog/">Blog</a>
    </div>
  </div>
</nav>"""


def footer_html():
    return """<footer>
  <div class="container">
    <div class="footer-links">
      <a href="/dubai/">Dubai</a>
      <a href="/abu-dhabi/">Abu Dhabi</a>
      <a href="/sharjah/">Sharjah</a>
      <a href="/ajman/">Ajman</a>
      <a href="/al-ain/">Al Ain</a>
      <a href="/ras-al-khaimah/">RAK</a>
      <a href="/fujairah/">Fujairah</a>
      <a href="/umm-al-quwain/">UAQ</a>
    </div>
    <div class="footer-links">
      <a href="/choose-number/">Browse Numbers</a>
      <a href="/home-wireless/">Home Internet</a>
      <a href="/faq/">FAQ</a>
      <a href="/about/">About</a>
      <a href="/privacy/">Privacy</a>
      <a href="/terms/">Terms</a>
      <a href="/refund-policy/">Refund Policy</a>
    </div>
    <div>&copy; 2026 goldennummbers.com. Authorized Etisalat Dealer, UAE.</div>
    <div style="margin-top:0.5rem;font-size:0.75rem;opacity:0.5;">Last updated: June 2026</div>
  </div>
</footer>"""


def wa_btn(href, label, extra=""):
    return (f'<a href="{href}" class="btn btn-wa-green" target="_blank" rel="noopener noreferrer"{extra}>'
            f'{WA_SVG} {label}</a>')


def sticky_cta(wa_href, second_href, second_label):
    return f"""<!-- GN STICKY CTA -->
<div class="gn-cta-sticky">
  <a class="gn-cta-wa" href="{wa_href}" target="_blank" rel="noopener">{WA_SVG}Talk to a LIVE Etisalat Agent</a>
  <a class="gn-cta-browse" href="{second_href}">{second_label}</a>
</div>"""


def trust_strip(items):
    svg_shield = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>'
    svg_truck = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>'
    svg_clock = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
    svg_wifi = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>'
    icons = {"shield": svg_shield, "truck": svg_truck, "clock": svg_clock, "wifi": svg_wifi}
    inner = "\n    ".join(f'<div class="trust-item">{icons[i]} {t}</div>' for i, t in items)
    return f'<div class="trust-strip">\n  <div class="container">\n    {inner}\n  </div>\n</div>'


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def faq_jsonld(faqs):
    return json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs],
    }, ensure_ascii=False)


def head_block(title, desc, keywords, slug, name, region, lat, lng, faqs, biz_desc, price_range):
    canonical = f"{BASE}/{slug}/"
    local_biz = json.dumps({
        "@context": "https://schema.org", "@type": "LocalBusiness",
        "name": f"Golden Numbers UAE, {name}", "description": biz_desc, "url": canonical,
        "telephone": "+971569028087",
        "address": {"@type": "PostalAddress", "addressCountry": "AE", "addressLocality": name},
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
        "areaServed": {"@type": "City", "name": name}, "priceRange": price_range,
        "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "09:00", "closes": "22:00"},
        "contactPoint": {"@type": "ContactPoint", "telephone": "+971569028087",
                         "contactType": "sales", "availableLanguage": ["English", "Arabic"]},
        "sameAs": ["https://www.facebook.com/share/17heRMZa83/", "https://www.instagram.com/consultant.ae",
                   "https://www.tiktok.com/@telecom.store.uae",
                   "https://whatsapp.com/channel/0029VbBycL87DAX2kICPBQ0S"],
    }, ensure_ascii=False)
    breadcrumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": canonical}],
    }, ensure_ascii=False)
    return f"""{HEAD_TRACKING}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta name="theme-color" content="#0D1117">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="goldennummbers.com">
<link rel="canonical" href="{canonical}">

<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="goldennummbers.com">
<meta property="og:locale" content="en_AE">
<meta property="og:image" content="{BASE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">

<meta name="geo.region" content="{region}">
<meta name="geo.placename" content="{name}, United Arab Emirates">
<meta name="geo.position" content="{lat};{lng}">
<meta name="ICBM" content="{lat}, {lng}">

<script type="application/ld+json">{local_biz}</script>
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{faq_jsonld(faqs)}</script>

<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">

{FB_PIXEL}
<style>
{CSS}
</style>"""


def faq_section(faqs):
    items = "\n".join(
        f'      <div class="faq-item">\n        <h3>{q}</h3>\n        <p>{a}</p>\n      </div>' for q, a in faqs)
    return f"""<section style="background:var(--surface);border-top:1px solid var(--surface-border);">
  <div class="container">
    <div class="section-heading"><h2>Frequently Asked Questions</h2></div>
    <div style="max-width:750px;margin:0 auto;">
{items}
    </div>
  </div>
</section>"""


def areas_section(name, areas, lead):
    tags = "\n      ".join(f'<span class="area-tag">{a}</span>' for a in areas)
    return f"""<section>
  <div class="container">
    <div class="section-heading">
      <h2>Areas We Serve in {name}</h2>
      <p>{lead}</p>
    </div>
    <div class="areas">
      {tags}
    </div>
  </div>
</section>"""


def page_end(wa_href, second_href, second_label, track_label, slug):
    return f"""{footer_html()}

{sticky_cta(wa_href, second_href, second_label)}

<script src="/assets/tracking.js" defer></script>
<script>
document.addEventListener('click', function(e) {{
  var link = e.target.closest('a[href*="wa.me"]');
  if (link && window.GN) window.GN.trackWhatsAppClick('{track_label}', '/{slug}/');
}});
</script>
</body>
</html>"""


# ---------- page builders ----------

def build_numbers(loc):
    name, slug = loc["name"], loc["slug"]
    title = f"VIP Numbers {name} | Etisalat Gold, Silver &amp; Platinum, Golden Numbers UAE"
    desc = (f"Buy Etisalat VIP mobile numbers in {name}, Gold, Silver & Platinum patterns with postpaid plans "
            f"from AED 188/mo. Authorized Etisalat dealer, free SIM delivery across {name}. WhatsApp +971 56 902 8087.")
    keywords = (f"VIP numbers {name}, Etisalat VIP number {name}, gold number {name}, buy VIP number {name}, "
                f"premium mobile numbers {name}, fancy numbers {name}, Etisalat postpaid {name}")
    a0, a1, a2 = loc["areas"][0], loc["areas"][1], loc["areas"][2]
    faqs = [
        (f"Where can I buy an Etisalat VIP number in {name}?",
         f"Order online at goldennummbers.com/choose-number/ or WhatsApp our live specialist at +971 56 902 8087. "
         f"We are an authorized Etisalat dealer with free SIM delivery across {name}, including {a0}, {a1} and {a2}."),
        (f"Do you deliver Etisalat SIMs to {a0}?",
         f"Yes. {loc['hook']} Delivery is free and there is no store visit, Emirates ID is the only document needed."),
        (f"How much does a golden number cost in {name}?",
         f"There is no one-time purchase price, the number is free with an Etisalat postpaid plan: Silver from AED 188/month "
         f"(unlimited data + 1,000 minutes), Gold AED 500/month (unlimited data + 3,000 minutes), Platinum AED 1,000/month "
         f"(unlimited data + unlimited calls). Prices exclude 5% VAT."),
        (f"Can I see available numbers before ordering in {name}?",
         f"Yes, browse 2,500+ live Etisalat numbers at goldennummbers.com/choose-number/, search by pattern "
         f"(777, 786, 1234…) and reserve online in two minutes. No payment is taken online."),
        (f"Can I port my du number to Etisalat in {name}?",
         f"Yes, Mobile Number Portability works everywhere in UAE including {name}. The switch takes 2-3 business days "
         f"and we handle the paperwork. Message us on WhatsApp to start."),
    ]
    hero_ctas = (wa_btn(WA_NUM, "Talk to a LIVE Etisalat Specialist Agent Now")
                 + '\n      <a href="/choose-number/" class="btn btn-outline">Browse Numbers</a>')
    body = f"""<section class="hero">
  <div class="container">
    <div style="display:inline-block;background:rgba(201,169,98,0.12);border:1px solid rgba(201,169,98,0.3);padding:0.35rem 1rem;border-radius:20px;font-size:0.8rem;color:var(--gold);margin-bottom:1.25rem;font-weight:600;">Authorized Etisalat Dealer, {name}</div>
    <h1>Etisalat VIP Numbers in <span>{name}</span></h1>
    <p>{loc['intro']}</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {hero_ctas}
    </div>
  </div>
</section>

{trust_strip([("shield", "Authorized Etisalat Dealer"), ("truck", f"Free Delivery in {name}"), ("clock", "Same-Day Activation"), ("shield", "No Online Payment")])}

<section>
  <div class="container">
    <div class="section-heading">
      <h2>Silver, Gold &amp; Platinum Numbers in {name}</h2>
      <p>Every number comes free with an Etisalat <strong>postpaid</strong> plan (monthly billing, no one-time number fee). +5% VAT.</p>
    </div>
    <div class="tier-grid">
      <div class="tier-card">
        <h3 style="color:silver;">Silver</h3>
        <div class="tc-price">AED 188<small>/month</small></div>
        <p>Unlimited data + 1,000 minutes. Memorable repeating patterns, free with the plan.</p>
        <a href="/choose-number/" class="btn btn-outline" style="font-size:0.85rem;padding:0.6rem 1.2rem;">Browse Silver Numbers</a>
      </div>
      <div class="tier-card" style="border-color:var(--gold);">
        <h3 style="color:var(--gold);">Gold</h3>
        <div class="tc-price">AED 500<small>/month</small></div>
        <p>Unlimited data + 3,000 minutes. Sequential and mirror patterns that customers remember.</p>
        <a href="/choose-number/" class="btn btn-outline" style="font-size:0.85rem;padding:0.6rem 1.2rem;">Browse Gold Numbers</a>
      </div>
      <div class="tier-card">
        <h3 style="color:#E5E4E2;">Platinum</h3>
        <div class="tc-price">AED 1,000<small>/month</small></div>
        <p>Unlimited data + unlimited calls. Hand-picked elite patterns, triple and quad repeats.</p>
        <a href="/choose-number/" class="btn btn-outline" style="font-size:0.85rem;padding:0.6rem 1.2rem;">Browse Platinum Numbers</a>
      </div>
    </div>
  </div>
</section>

{areas_section(name, loc['areas'], f"Free SIM delivery to every neighborhood, no store visit needed. {loc['hook']}")}

<section style="background:var(--surface);border-top:1px solid var(--surface-border);border-bottom:1px solid var(--surface-border);">
  <div class="container" style="text-align:center;">
    <div class="section-heading">
      <h2>Need Home Internet in {name} Too?</h2>
      <p>5.5G Wireless Home Internet, unlimited data, FREE AED 800 router, no upfront payment, delivered free within 24 hours.</p>
    </div>
    <a href="/home-internet-{slug}/" class="btn btn-gold">Home Internet in {name} &rarr;</a>
  </div>
</section>

{faq_section(faqs)}

<section class="cta-section">
  <div class="container">
    <h2 style="font-family:var(--font-heading);font-size:1.9rem;margin-bottom:0.75rem;">Get Your VIP Number in {name} Today</h2>
    <p style="color:var(--text-muted);margin-bottom:2rem;">Free delivery, same-day activation, no payment online.</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {hero_ctas}
    </div>
    <div style="margin-top:1rem;color:var(--text-muted);font-size:0.85rem;">WhatsApp: +971 56 902 8087 &nbsp;&middot;&nbsp; Calls: +971 56 902 8087</div>
  </div>
</section>"""
    head = head_block(title, desc, keywords, slug, name, loc["region"], loc["lat"], loc["lng"], faqs,
                      f"Authorized Etisalat dealer serving {name}. VIP Gold, Silver and Platinum numbers with postpaid plans and free SIM delivery.",
                      "AED 188 - AED 1,000")
    return (f"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n{head}\n</head>\n<body>\n{EC_BAR}\n{nav_html()}\n\n{body}\n\n"
            + page_end(WA_NUM, "/choose-number/", "Browse Numbers", f"{name} Numbers Page", slug))


def build_internet(loc):
    name, slug = loc["name"], loc["slug"]
    title = f"Home Internet {name} | 5.5G Wireless WiFi, No Landline, Free 24h Delivery"
    desc = (f"5.5G wireless home internet in {name}, unlimited data from AED 206/mo, no landline, no installation. "
            f"FREE AED 800 router, no upfront payment, free delivery within 24 hours across {name}. WhatsApp +971 56 902 8087.")
    keywords = (f"home internet {name}, wifi connection {name}, internet without landline {name}, 5G home internet {name}, "
                f"5.5G internet {name}, Etisalat home wireless {name}, internet plans {name}")
    a0, a1, a2 = loc["areas"][0], loc["areas"][1], loc["areas"][2]
    faqs = [
        (f"How do I get home internet in {name} without a landline?",
         f"Order Etisalat 5.5G Home Wireless, no landline, no fiber cabling, no technician. The router is delivered free "
         f"within 24 hours anywhere in {name} (including {a0}, {a1} and {a2}); plug it into power and your WiFi is live. "
         f"Reserve at goldennummbers.com/home-wireless/ or WhatsApp +971 56 902 8087."),
        (f"How much does home internet cost in {name}?",
         f"Two plans: Advance (super-fast internet) at AED 206/month promotional with a 12-month commitment, and Premium "
         f"(full-speed unlimited + FREE StarzPlay) at AED 269/month promotional with a 24-month commitment. Both have "
         f"unlimited local data and exclude 5% VAT. No upfront payment, and the AED 800 router is free."),
        (f"How fast can I get connected in {name}?",
         f"Typically within 24 hours of ordering. {loc['hook']} There is no installation appointment, setup is plugging "
         f"the router into a power socket."),
        (f"Is the data really unlimited?",
         f"Yes, both plans include unlimited local data for home use, with no monthly cap. Premium adds a free StarzPlay "
         f"subscription for movies and entertainment."),
        (f"Can I move my router to a new home in {name}?",
         f"Yes, the router is not tied to an installed address. Take it with you when you move and plug it in at the new "
         f"home. Confirm coverage at the new address with our specialist on WhatsApp first."),
    ]
    hero_ctas = (wa_btn(WA_HW, "Talk to a LIVE Etisalat Specialist Agent Now")
                 + '\n      <a href="/home-wireless/" class="btn btn-outline">Explore Home Internet Plans</a>')
    cross = loc.get("cross")
    cross_section = f"""<section style="background:var(--surface);border-top:1px solid var(--surface-border);border-bottom:1px solid var(--surface-border);">
  <div class="container" style="text-align:center;">
    <div class="section-heading">
      <h2>Need a VIP Mobile Number in {name} Too?</h2>
      <p>Silver, Gold &amp; Platinum Etisalat numbers, free with postpaid plans from AED 188/month. One delivery, one specialist.</p>
    </div>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      <a href="/{cross}/" class="btn btn-gold">VIP Numbers in {name} &rarr;</a>
      <a href="/choose-number/" class="btn btn-outline">Browse Numbers</a>
    </div>
  </div>
</section>""" if cross else ""
    body = f"""<section class="hero">
  <div class="container">
    <div style="display:inline-block;background:rgba(201,169,98,0.12);border:1px solid rgba(201,169,98,0.3);padding:0.35rem 1rem;border-radius:20px;font-size:0.8rem;color:var(--gold);margin-bottom:1.25rem;font-weight:600;">Authorized Etisalat Dealer, {name}</div>
    <h1>5.5G Home Internet in <span>{name}</span>, No Landline Needed</h1>
    <p>{loc['intro']}</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {hero_ctas}
    </div>
  </div>
</section>

{trust_strip([("wifi", "Unlimited Local Data"), ("truck", f"Free 24h Delivery in {name}"), ("clock", "Plug & Play, No Installation"), ("shield", "No Upfront Payment")])}

<section>
  <div class="container">
    <div class="section-heading">
      <h2>💎 Choose Your Plan in {name}</h2>
      <p>Prices exclude 5% VAT. Promotional pricing as listed by Etisalat, full details &amp; online reservation on the <a href="/home-wireless/" style="color:var(--gold);">Home Wireless page</a>.</p>
    </div>
    <div class="tier-grid" style="max-width:820px;">
      <div class="tier-card">
        <h3>🚀 Advance</h3>
        <div style="color:var(--gold);font-size:0.85rem;font-weight:600;margin-bottom:0.3rem;">Super-Fast Internet</div>
        <div class="tc-price">AED 206<small>/month &middot; 12-mo commitment</small></div>
        <p>Unlimited local data &middot; optional 5G router &middot; GoChat unlimited voice &amp; video calls.</p>
        <a href="/home-wireless/" class="btn btn-gold" style="font-size:0.85rem;padding:0.6rem 1.4rem;">Reserve Advance &rarr;</a>
      </div>
      <div class="tier-card" style="border-color:var(--gold);">
        <h3>👑 Premium</h3>
        <div style="color:var(--gold);font-size:0.85rem;font-weight:600;margin-bottom:0.3rem;">Full-Speed Unlimited &middot; 🎬 FREE StarzPlay</div>
        <div class="tc-price">AED 269<small>/month &middot; 24-mo commitment</small></div>
        <p>Unlimited local data &middot; STARZPLAY included &middot; free GoChat Premium.</p>
        <a href="/home-wireless/" class="btn btn-gold" style="font-size:0.85rem;padding:0.6rem 1.4rem;">Reserve Premium &rarr;</a>
      </div>
    </div>
  </div>
</section>

<section style="background:linear-gradient(135deg,rgba(201,169,98,0.10),rgba(201,169,98,0.03));border-top:1px solid var(--surface-border);border-bottom:1px solid var(--surface-border);">
  <div class="container" style="text-align:center;">
    <div class="section-heading">
      <h2>🔥 Why {name} Homes Choose 5.5G</h2>
    </div>
    <div class="check-grid">
      <div>✅ No Upfront Payment</div>
      <div>✅ FREE AED 800 Router</div>
      <div>✅ FREE Delivery Within 24 Hours</div>
      <div>✅ 14-Day Free Grace Period</div>
      <div>✅ Plug &amp; Play Setup</div>
      <div>✅ Super-Fast 5.5G Technology</div>
      <div>✅ No Installation Delays</div>
    </div>
    {wa_btn(WA_HW, "Talk to a LIVE Etisalat Specialist Agent Now")}
  </div>
</section>

{areas_section(name, loc['areas'], f"Free router delivery within 24 hours, no installation visit. {loc['hook']}")}

{cross_section}

{faq_section(faqs)}

<section class="cta-section">
  <div class="container">
    <h2 style="font-family:var(--font-heading);font-size:1.9rem;margin-bottom:0.75rem;">📲 Get {name} Online Tomorrow</h2>
    <p style="color:var(--text-muted);margin-bottom:2rem;">Upgrade your home internet today and enjoy the speed UAE deserves. 🚚 FREE delivery within 24 hours.</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {hero_ctas}
    </div>
    <div style="margin-top:1rem;color:var(--text-muted);font-size:0.85rem;">WhatsApp: +971 56 902 8087 &nbsp;&middot;&nbsp; Calls: +971 56 902 8087</div>
  </div>
</section>"""
    head = head_block(title, desc, keywords, slug, name, loc["region"], loc["lat"], loc["lng"], faqs,
                      f"Authorized Etisalat dealer, 5.5G wireless home internet in {name} with unlimited data, free router and free 24-hour delivery.",
                      "AED 206 - AED 269")
    return (f"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n{head}\n</head>\n<body>\n{EC_BAR}\n{nav_html()}\n\n{body}\n\n"
            + page_end(WA_HW, "/home-wireless/", "Explore Internet Plans", f"{name} Internet Page", slug))


def build_area(loc):
    name, slug = loc["name"], loc["slug"]
    title = f"Etisalat VIP Numbers &amp; Home Internet in {name} | Same-Day Delivery, Golden Numbers UAE"
    desc = (f"Etisalat services in {name}, Dubai, VIP Gold/Silver/Platinum numbers from AED 188/mo and 5.5G wireless "
            f"home internet from AED 206/mo. Free same-day delivery to {name}. Authorized dealer. WhatsApp +971 56 902 8087.")
    keywords = (f"Etisalat {name}, VIP number {name}, golden number {name}, home internet {name}, wifi {name}, "
                f"Etisalat SIM delivery {name}, Etisalat dealer {name}")
    a0, a1 = loc["areas"][0], loc["areas"][1]
    faqs = [
        (f"Does goldennummbers.com deliver to {name}?",
         f"Yes, free delivery across {name} including {a0} and {a1}. {loc['hook']}"),
        (f"How do I get an Etisalat VIP number in {name}?",
         f"Browse 2,500+ live numbers at goldennummbers.com/choose-number/ and reserve online, or WhatsApp our live "
         f"specialist at +971 56 902 8087. The number is free with an Etisalat postpaid plan from AED 188/month; "
         f"the SIM is delivered free to your address in {name}."),
        (f"Can I get home internet in {name} without installation?",
         f"Yes, Etisalat 5.5G Home Wireless needs no landline, no cabling and no technician. The router (worth AED 800, "
         f"free with the plan) is delivered to {name} within 24 hours; plug it in and your unlimited WiFi is live. "
         f"Plans from AED 206/month at goldennummbers.com/home-wireless/."),
        (f"What documents do I need for delivery in {name}?",
         f"Emirates ID only, for both VIP numbers and home internet. No store visit, no paperwork hassle; "
         f"the Etisalat verification department calls you to confirm."),
        (f"How fast is delivery to {name}?",
         f"SIM deliveries are typically same-day; home internet routers arrive within 24 hours. "
         f"Confirm your slot with the specialist on WhatsApp +971 56 902 8087."),
    ]
    num_ctas = (wa_btn(WA_NUM, "Talk to a LIVE Etisalat Specialist Agent Now")
                + '\n      <a href="/choose-number/" class="btn btn-outline">Browse Numbers</a>')
    hw_ctas = (wa_btn(WA_HW, "Talk to a LIVE Etisalat Specialist Agent Now")
               + '\n      <a href="/home-wireless/" class="btn btn-outline">Explore Home Internet Plans</a>')
    body = f"""<section class="hero">
  <div class="container">
    <div style="display:inline-block;background:rgba(201,169,98,0.12);border:1px solid rgba(201,169,98,0.3);padding:0.35rem 1rem;border-radius:20px;font-size:0.8rem;color:var(--gold);margin-bottom:1.25rem;font-weight:600;">Authorized Etisalat Dealer, {name}, Dubai</div>
    <h1>Etisalat VIP Numbers &amp; Home Internet in <span>{name}</span></h1>
    <p>{loc['intro']}</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {num_ctas}
    </div>
  </div>
</section>

{trust_strip([("shield", "Authorized Etisalat Dealer"), ("truck", f"Free Same-Day Delivery in {name}"), ("clock", "Same-Day Activation"), ("wifi", "5.5G Home Internet")])}

<section>
  <div class="container">
    <div class="section-heading">
      <h2>VIP Golden Numbers in {name}</h2>
      <p>Silver from AED 188/mo &middot; Gold AED 500/mo &middot; Platinum AED 1,000/mo, the number is free with the Etisalat <strong>postpaid</strong> plan. +5% VAT.</p>
    </div>
    <div style="display:flex;gap:0.6rem;justify-content:center;flex-wrap:wrap;margin-bottom:1.75rem;">
      <span class="area-tag">050 XXX 7777</span>
      <span class="area-tag">054 X 786 786</span>
      <span class="area-tag">056 XXX 1234</span>
      <span class="area-tag">050 XXX 0000</span>
      <span class="area-tag">055 XX 88888</span>
    </div>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {num_ctas}
    </div>
  </div>
</section>

<section style="background:linear-gradient(135deg,rgba(201,169,98,0.10),rgba(201,169,98,0.03));border-top:1px solid var(--surface-border);border-bottom:1px solid var(--surface-border);">
  <div class="container" style="text-align:center;">
    <div class="section-heading">
      <h2>5.5G Wireless Home Internet in {name}</h2>
      <p>🚀 Advance, Super-Fast Internet, <strong>AED 206/mo</strong> &nbsp;|&nbsp; 👑 Premium, Full-Speed Unlimited + 🎬 FREE StarzPlay, <strong>AED 269/mo</strong></p>
    </div>
    <div class="check-grid">
      <div>✅ No Upfront Payment</div>
      <div>✅ FREE AED 800 Router</div>
      <div>✅ FREE Delivery Within 24 Hours</div>
      <div>✅ 14-Day Free Grace Period</div>
      <div>✅ Plug &amp; Play, No Installation</div>
      <div>✅ Unlimited Local Data</div>
    </div>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {hw_ctas}
    </div>
  </div>
</section>

{areas_section(name, loc['areas'], f"Free delivery across {name}, no store visit needed. {loc['hook']}")}

{faq_section(faqs)}

<section class="cta-section">
  <div class="container">
    <h2 style="font-family:var(--font-heading);font-size:1.9rem;margin-bottom:0.75rem;">Set Up in {name} Today</h2>
    <p style="color:var(--text-muted);margin-bottom:2rem;">VIP number, home internet, or both, one specialist, free delivery, Emirates ID only.</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
      {num_ctas}
    </div>
    <div style="margin-top:1rem;color:var(--text-muted);font-size:0.85rem;">WhatsApp: +971 56 902 8087 &nbsp;&middot;&nbsp; Calls: +971 56 902 8087</div>
  </div>
</section>"""
    head = head_block(title, desc, keywords, slug, name, loc["region"], loc["lat"], loc["lng"], faqs,
                      f"Authorized Etisalat dealer serving {name}, Dubai, VIP numbers and 5.5G home internet with free same-day delivery.",
                      "AED 188 - AED 1,000")
    return (f"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n{head}\n</head>\n<body>\n{EC_BAR}\n{nav_html()}\n\n{body}\n\n"
            + page_end(WA_NUM, "/choose-number/", "Browse Numbers", f"{name} Area Page", slug))


BUILDERS = {"numbers": build_numbers, "internet": build_internet, "area": build_area}

written = []
for loc in LOCATIONS:
    html = BUILDERS[loc["kind"]](loc)
    out = ROOT / loc["slug"] / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    written.append((loc["kind"], loc["slug"], len(html)))

for kind, slug, size in written:
    print(f"{kind:9s} /{slug}/ ({size:,} bytes)")
print(f"\ntotal: {len(written)} pages")
