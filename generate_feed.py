"""
Generate Meta/Google product feed for Etisalat Golden Numbers.

Pulls available numbers from the live Google Sheet, renders a card PNG per
number into cards/<with_zero>.png matching the existing card design (gold
corners, serif number, category badge, QR code), and writes feed.xml at
the repo root.

Cloudflare Pages serves the repo as static assets, so after `git push`:
  https://etisalat.shop/feed.xml
  https://etisalat.shop/cards/<with_zero>.png

Configure in Meta:
  Commerce Manager -> Catalog -> Data sources -> Scheduled feed
  URL: https://etisalat.shop/feed.xml   refresh: daily
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import qrcode
import qrcode.constants
from PIL import Image, ImageDraw, ImageFont

# ---- Config ---------------------------------------------------------------

# Both inventory sheets — same pair the /choose-number/ pages + generate_number_pages.py consume.
SHEETS = [
    {"id": "1qAw1YQkKEbq-R3LullCBNr0MweGfC2KEO-rot9ff8dw", "gid": "0"},
    {"id": "1Lmfsc-0H0R0hXv0wddktRwisHI74yu9JfrtxPajm9hk", "gid": "0"},
]
SITE_URL = "https://goldennummbers.com"
ROOT = Path(__file__).resolve().parent
CARDS_DIR = ROOT / "cards"
FEED_PATH = ROOT / "feed.xml"

BG = (13, 17, 23)
GOLD = (201, 169, 98)
GOLD_LIGHT = (232, 213, 163)
WHITE = (245, 245, 240)
MUTED = (160, 160, 155)

PRICE_GOLD = 500
PRICE_SILVER = 188

CARD_W, CARD_H = 1080, 1080
GOOGLE_CATEGORY = "Electronics > Communications > Telephony > Mobile Phones"


# ---- Sheet ----------------------------------------------------------------

def fetch_sheet() -> list[dict]:
    """Fetch + concatenate all configured sheets, de-duped by MSISDN (first wins)."""
    rows: list[dict] = []
    seen: set[str] = set()
    for sh in SHEETS:
        url = (
            f"https://docs.google.com/spreadsheets/d/{sh['id']}"
            f"/gviz/tq?tqx=out:csv&headers=1&gid={sh['gid']}"
        )
        req = urllib.request.Request(
            url, headers={"User-Agent": "etisalat-shop/feed-generator"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read().decode("utf-8-sig")
        for row in csv.DictReader(io.StringIO(data)):
            msisdn = (row.get("MSISDN") or "").strip()
            if msisdn and msisdn in seen:
                continue
            if msisdn:
                seen.add(msisdn)
            rows.append(row)
    return rows


def format_number(with_zero: str) -> str:
    """0569888791 -> 056 988 8791"""
    digits = "".join(ch for ch in (with_zero or "") if ch.isdigit())
    if len(digits) == 10 and digits.startswith("0"):
        return f"{digits[:3]} {digits[3:6]} {digits[6:]}"
    return digits


def category_norm(category: str) -> str:
    cat = (category or "").strip().lower()
    if "gold" in cat:
        return "Gold"
    if "silver" in cat:
        return "Silver Plus" if "plus" in cat else "Silver"
    return category.strip().title() or "Standard"


def price_aed(category: str) -> int:
    return PRICE_GOLD if "gold" in (category or "").lower() else PRICE_SILVER


# ---- Font loading ---------------------------------------------------------

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        if bold
        else [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def load_serif_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            "C:/Windows/Fonts/cambriab.ttf",
            "C:/Windows/Fonts/georgiab.ttf",
            "C:/Windows/Fonts/palab.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ]
        if bold
        else [
            "C:/Windows/Fonts/cambria.ttc",
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/pala.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return load_font(size, bold)


# ---- Card rendering -------------------------------------------------------

def _corner_brackets(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    length: int,
    thickness: int,
    inset: int,
    color: tuple,
) -> None:
    # top-left
    draw.line([(inset, inset), (inset + length, inset)], fill=color, width=thickness)
    draw.line([(inset, inset), (inset, inset + length)], fill=color, width=thickness)
    # top-right
    draw.line([(w - inset - length, inset), (w - inset, inset)], fill=color, width=thickness)
    draw.line([(w - inset, inset), (w - inset, inset + length)], fill=color, width=thickness)
    # bottom-left
    draw.line([(inset, h - inset - length), (inset, h - inset)], fill=color, width=thickness)
    draw.line([(inset, h - inset), (inset + length, h - inset)], fill=color, width=thickness)
    # bottom-right
    draw.line([(w - inset - length, h - inset), (w - inset, h - inset)], fill=color, width=thickness)
    draw.line([(w - inset, h - inset - length), (w - inset, h - inset)], fill=color, width=thickness)


def render_card(
    formatted: str,
    category: str,
    price: int,
    qr_url: str,
    out_path: Path,
) -> None:
    img = Image.new("RGB", (CARD_W, CARD_H), BG)
    draw = ImageDraw.Draw(img)

    # subtle top-down gradient
    for y in range(CARD_H):
        t = y / CARD_H
        rgb = (
            int(BG[0] + 6 * (1 - t)),
            int(BG[1] + 8 * (1 - t)),
            int(BG[2] + 10 * (1 - t)),
        )
        draw.line([(0, y), (CARD_W, y)], fill=rgb)

    _corner_brackets(draw, CARD_W, CARD_H, length=70, thickness=2, inset=50, color=GOLD)

    f_avail = load_font(28, bold=True)
    avail_text = "AVAILABLE   NOW"
    bb = f_avail.getbbox(avail_text)
    aw = bb[2] - bb[0]
    draw.text(((CARD_W - aw) // 2, 145), avail_text, fill=GOLD_LIGHT, font=f_avail)
    underline_w = aw // 2
    draw.line(
        [((CARD_W - underline_w) // 2, 192), ((CARD_W + underline_w) // 2, 192)],
        fill=GOLD,
        width=2,
    )

    # Big serif number — auto-shrink if too wide
    num_size = 150
    f_num = load_serif_font(num_size, bold=True)
    bb = f_num.getbbox(formatted)
    nw, nh = bb[2] - bb[0], bb[3] - bb[1]
    while nw > CARD_W - 100 and num_size > 80:
        num_size -= 10
        f_num = load_serif_font(num_size, bold=True)
        bb = f_num.getbbox(formatted)
        nw, nh = bb[2] - bb[0], bb[3] - bb[1]
    num_y = 320
    draw.text(((CARD_W - nw) // 2, num_y), formatted, fill=GOLD_LIGHT, font=f_num)

    # Category pill
    f_cat = load_font(28, bold=True)
    cat_text = category.upper()
    bb = f_cat.getbbox(cat_text)
    cw, ch = bb[2] - bb[0], bb[3] - bb[1]
    pad_x, pad_y = 26, 9
    box_w = cw + pad_x * 2
    box_h = ch + pad_y * 2
    box_x = (CARD_W - box_w) // 2
    box_y = num_y + nh + 55
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=box_h // 2,
        outline=GOLD,
        width=2,
    )
    draw.text(
        (box_x + pad_x, box_y + pad_y - bb[1]),
        cat_text,
        fill=GOLD,
        font=f_cat,
    )

    f_book = load_font(24)
    book_text = "Booking open   |   Call or WhatsApp"
    bb = f_book.getbbox(book_text)
    bw = bb[2] - bb[0]
    book_y = box_y + box_h + 40
    draw.text(((CARD_W - bw) // 2, book_y), book_text, fill=WHITE, font=f_book)

    f_wa_big = load_serif_font(38)
    wa_text = "+971 56 699 9377"
    bb = f_wa_big.getbbox(wa_text)
    ww = bb[2] - bb[0]
    draw.text(
        ((CARD_W - ww) // 2, book_y + 36),
        wa_text,
        fill=WHITE,
        font=f_wa_big,
    )

    sep_w = 460
    sep_y = book_y + 95
    draw.line(
        [((CARD_W - sep_w) // 2, sep_y), ((CARD_W + sep_w) // 2, sep_y)],
        fill=GOLD,
        width=1,
    )

    f_scan = load_font(20)
    scan_text = "or scan to view this number online"
    bb = f_scan.getbbox(scan_text)
    sw = bb[2] - bb[0]
    draw.text(
        ((CARD_W - sw) // 2, sep_y + 24),
        scan_text,
        fill=MUTED,
        font=f_scan,
    )

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_size = 270
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = (CARD_W - qr_size) // 2
    qr_y = sep_y + 64
    pad = 14
    draw.rounded_rectangle(
        [qr_x - pad, qr_y - pad, qr_x + qr_size + pad, qr_y + qr_size + pad],
        radius=10,
        fill=(255, 255, 255),
    )
    img.paste(qr_img, (qr_x, qr_y))

    f_foot_label = load_font(16)
    f_foot_main = load_font(22, bold=True)
    foot_y = CARD_H - 65
    draw.text((70, foot_y), "goldennummbers.com", fill=GOLD, font=f_foot_main)

    label_text = "WHATSAPP"
    main_text = "+971 56 699 9377"
    bb_label = f_foot_label.getbbox(label_text)
    bb_main = f_foot_main.getbbox(main_text)
    label_w = bb_label[2] - bb_label[0]
    main_w = bb_main[2] - bb_main[0]
    right_edge = CARD_W - 70
    draw.text(
        (right_edge - label_w, foot_y - 22),
        label_text,
        fill=MUTED,
        font=f_foot_label,
    )
    draw.text(
        (right_edge - main_w, foot_y),
        main_text,
        fill=GOLD,
        font=f_foot_main,
    )

    img.save(out_path, "PNG", optimize=True)


# ---- Feed XML -------------------------------------------------------------

def build_feed(products: list[dict]) -> ET.ElementTree:
    NS_G = "http://base.google.com/ns/1.0"
    ET.register_namespace("g", NS_G)
    rss = ET.Element("rss", {"version": "2.0", "xmlns:g": NS_G})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Etisalat Golden Numbers"
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = (
        "VIP Etisalat postpaid phone numbers — UAE. "
        "Numbers free with monthly plan."
    )
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(
        timezone.utc
    ).strftime("%a, %d %b %Y %H:%M:%S +0000")

    for p in products:
        item = ET.SubElement(channel, "item")
        for tag, val in [
            ("g:id", p["id"]),
            ("title", p["title"]),
            ("description", p["description"]),
            ("link", p["link"]),
            ("g:image_link", p["image_link"]),
            ("g:availability", p["availability"]),
            ("g:condition", p["condition"]),
            ("g:price", p["price"]),
            ("g:brand", p["brand"]),
            ("g:product_type", p["product_type"]),
            ("g:google_product_category", p["google_product_category"]),
            ("g:identifier_exists", "no"),
        ]:
            ET.SubElement(item, tag).text = val

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    return tree


# ---- Main -----------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="Re-render all cards")
    ap.add_argument(
        "--no-images", action="store_true", help="Skip card rendering, build feed only"
    )
    ap.add_argument(
        "--limit", type=int, default=0, help="Cap number of products (debug)"
    )
    args = ap.parse_args()

    print(f"Fetching {len(SHEETS)} sheet(s)")
    rows = fetch_sheet()
    print(f"  {len(rows)} total rows (de-duped across sheets)")

    available = [
        r for r in rows
        if (r.get("Status") or "").strip().lower() == "available"
    ]
    print(f"  {len(available)} available")

    if args.limit:
        available = available[: args.limit]
        print(f"  limited to {len(available)} (debug)")

    CARDS_DIR.mkdir(exist_ok=True)

    products: list[dict] = []
    rendered = skipped = errors = 0

    for i, row in enumerate(available, 1):
        msisdn = (row.get("MSISDN") or "").strip()
        with_zero = (row.get("With Zero") or "").strip()
        category_raw = (row.get("Category") or "").strip()
        if not msisdn or not with_zero:
            errors += 1
            continue

        formatted = format_number(with_zero)
        category = category_norm(category_raw)
        price = price_aed(category_raw)
        product_url = f"{SITE_URL}/choose-number/?n={with_zero}"
        card_path = CARDS_DIR / f"{with_zero}.png"

        if not args.no_images and (args.force or not card_path.exists()):
            try:
                render_card(formatted, category, price, product_url, card_path)
                rendered += 1
                if rendered % 50 == 0:
                    print(f"  ...rendered {rendered}/{len(available)}")
            except Exception as e:
                print(f"  [warn] render {with_zero} failed: {e}")
                errors += 1
                continue
        elif card_path.exists():
            skipped += 1

        title = f"Etisalat VIP Number {formatted} - {category}"
        description = (
            f"Premium Etisalat VIP number {formatted}. "
            f"Free with AED {price}/month postpaid plan. "
            f"Authorized Etisalat dealer in UAE. Inquire on WhatsApp."
        )
        products.append(
            {
                "id": msisdn,
                "title": title[:150],
                "description": description[:5000],
                "link": product_url,
                "image_link": f"{SITE_URL}/cards/{with_zero}.png",
                "availability": "in stock",
                "condition": "new",
                "price": f"{price}.00 AED",
                "brand": "Etisalat",
                "product_type": category,
                "google_product_category": GOOGLE_CATEGORY,
            }
        )

    print(f"  cards rendered: {rendered}, skipped (existing): {skipped}, errors: {errors}")

    if not products:
        print("  [error] no products to write")
        return 1

    tree = build_feed(products)
    tree.write(FEED_PATH, encoding="utf-8", xml_declaration=True)
    print(f"  feed: {FEED_PATH} ({len(products)} items, {FEED_PATH.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
