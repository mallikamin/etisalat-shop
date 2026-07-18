import hashlib
import io
import json
import os
import secrets
import sqlite3
from csv import DictWriter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import qrcode
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "partner_tracking.db"
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

APP_SALT = os.getenv("APP_SALT", "change-this-salt")
ADMIN_MOBILE = os.getenv("ADMIN_MOBILE", "971569028087")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-admin-password")
CHOOSE_NUMBER_URL = os.getenv("CHOOSE_NUMBER_URL", "https://etisalat.shop/choose-number/")
TOKEN_TTL_HOURS = int(os.getenv("TOKEN_TTL_HOURS", "24"))

app = FastAPI(title="Etisalat Partner Tracking API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/generated", StaticFiles(directory=str(GENERATED_DIR)), name="generated")


class PartnerRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    mobile: str = Field(min_length=7, max_length=20)
    address: str = Field(min_length=4, max_length=250)
    latitude: float
    longitude: float
    partner_type: str = Field(default="retail")


class PartnerLogin(BaseModel):
    mobile: str
    pin: str = Field(min_length=4, max_length=10)


class AdminLogin(BaseModel):
    mobile: str
    password: str


class EventTrack(BaseModel):
    event_type: str = Field(pattern="^(scan|whatsapp_click)$")
    ref_code: str = Field(min_length=3, max_length=60)
    lead_token: Optional[str] = None
    number: Optional[str] = None
    category: Optional[str] = None
    page: Optional[str] = None


class LeadUpdate(BaseModel):
    status: str = Field(pattern="^(new|contacted|won|lost)$")
    sale_amount: Optional[float] = None


class PartnerPinChange(BaseModel):
    current_pin: str = Field(min_length=4, max_length=10)
    new_pin: str = Field(min_length=4, max_length=10)


class AdminPartnerUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    address: Optional[str] = Field(default=None, min_length=4, max_length=250)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    partner_type: Optional[str] = None
    active: Optional[bool] = None


class AdminPartnerPinReset(BaseModel):
    new_pin: str = Field(min_length=4, max_length=10)


class CustomPdfRequest(BaseModel):
    width_in: float = Field(ge=2.0, le=60.0)
    height_in: float = Field(ge=2.0, le=60.0)
    label: str = Field(min_length=2, max_length=40)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_mobile(mobile: str) -> str:
    digits = "".join(ch for ch in mobile if ch.isdigit())
    if not digits:
        raise HTTPException(status_code=400, detail="Invalid mobile number")
    return digits


def hash_secret(raw: str) -> str:
    return hashlib.sha256(f"{APP_SALT}:{raw}".encode("utf-8")).hexdigest()


def normalize_partner_type(value: str) -> str:
    allowed = {"retail", "field", "reseller"}
    cleaned = (value or "").strip().lower()
    if cleaned not in allowed:
        raise HTTPException(status_code=400, detail="partner_type must be retail, field, or reseller")
    return cleaned


def extract_city(address: str) -> str:
    parts = [p.strip() for p in (address or "").split(",") if p.strip()]
    if not parts:
        return "unknown"
    return parts[-1][:60].lower()


def hash_ip(raw_ip: Optional[str]) -> Optional[str]:
    if not raw_ip:
        return None
    return hashlib.sha256(f"{APP_SALT}:ip:{raw_ip}".encode("utf-8")).hexdigest()


@contextmanager
def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ensure_schema() -> None:
    with db_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_type TEXT NOT NULL,
                name TEXT NOT NULL,
                mobile TEXT NOT NULL UNIQUE,
                pin_hash TEXT NOT NULL,
                address TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                ref_code TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                mobile TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER,
                role TEXT NOT NULL,
                partner_id INTEGER,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                ref_code TEXT NOT NULL,
                lead_token TEXT,
                number TEXT,
                category TEXT,
                page TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_token TEXT NOT NULL UNIQUE,
                ref_code TEXT NOT NULL,
                partner_id INTEGER,
                status TEXT NOT NULL DEFAULT 'new',
                sale_amount REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                closed_at TEXT
            );
            """
        )
        # Lightweight migrations for existing DB files.
        try:
            conn.execute("ALTER TABLE partners ADD COLUMN updated_at TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE events ADD COLUMN ip_hash TEXT")
        except sqlite3.OperationalError:
            pass

        admin = conn.execute("SELECT id FROM users WHERE mobile = ?", (clean_mobile(ADMIN_MOBILE),)).fetchone()
        if not admin:
            conn.execute(
                "INSERT INTO users (role, mobile, password_hash, name, created_at) VALUES (?, ?, ?, ?, ?)",
                ("admin", clean_mobile(ADMIN_MOBILE), hash_secret(ADMIN_PASSWORD), "Malik Amin", now_iso()),
            )
        conn.execute("UPDATE partners SET updated_at = COALESCE(updated_at, created_at)")


def make_ref_code(mobile: str) -> str:
    return f"p{mobile}"


def create_qr(ref_code: str) -> Dict[str, str]:
    tracked_url = f"{CHOOSE_NUMBER_URL}?ref={ref_code}"
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(tracked_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_file = GENERATED_DIR / f"{ref_code}.png"
    img.save(qr_file)
    return {
        "qr_file": f"/generated/{qr_file.name}",
        "tracked_url": tracked_url,
    }


def draw_partner_pdf(pdf_path: Path, ref_code: str, qr_file_path: Path, page_size: tuple[float, float], label: str) -> None:
    w, h = page_size
    c = canvas.Canvas(str(pdf_path), pagesize=(w, h))
    c.setFillColor(colors.HexColor("#fbf8f2"))
    c.rect(0, 0, w, h, stroke=0, fill=1)

    margin = min(w, h) * 0.06
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#ddd3c3"))
    c.roundRect(margin, margin, w - (2 * margin), h - (2 * margin), 12, stroke=1, fill=1)

    c.setFillColor(colors.HexColor("#1f2328"))
    c.setFont("Helvetica-Bold", min(w, h) * 0.06)
    c.drawCentredString(w / 2, h - margin - (min(w, h) * 0.14), "Choose Your Number")

    c.setFillColor(colors.HexColor("#5d6571"))
    c.setFont("Helvetica", min(w, h) * 0.03)
    c.drawCentredString(w / 2, h - margin - (min(w, h) * 0.18), "Scan for live VIP number search")

    qr_size = min(w, h) * 0.42
    qr_x = (w - qr_size) / 2
    qr_y = (h - qr_size) / 2 - (min(w, h) * 0.03)
    c.drawImage(str(qr_file_path), qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True)

    c.setFillColor(colors.HexColor("#2e2617"))
    c.setFont("Helvetica-Bold", min(w, h) * 0.032)
    c.drawCentredString(w / 2, qr_y - (min(w, h) * 0.04), "etisalat.shop/choose-number")

    c.setFillColor(colors.HexColor("#697382"))
    c.setFont("Helvetica", min(w, h) * 0.024)
    c.drawCentredString(w / 2, margin + (min(w, h) * 0.12), f"Agent Ref: {ref_code}")
    c.drawCentredString(w / 2, margin + (min(w, h) * 0.08), f"Template: {label}")
    c.drawCentredString(w / 2, margin + (min(w, h) * 0.04), "Authorized Etisalat Dealer")

    c.save()


def generate_assets(ref_code: str) -> Dict[str, Any]:
    qr_result = create_qr(ref_code)
    qr_file_path = GENERATED_DIR / f"{ref_code}.png"

    sizes = {
        "4x6": (4 * inch, 6 * inch),
        "a4": (8.27 * inch, 11.69 * inch),
        "square": (6 * inch, 6 * inch),
    }

    pdfs: Dict[str, str] = {}
    for label, page_size in sizes.items():
        pdf_name = f"{ref_code}-{label}.pdf"
        pdf_path = GENERATED_DIR / pdf_name
        draw_partner_pdf(pdf_path, ref_code, qr_file_path, page_size, label)
        pdfs[label] = f"/generated/{pdf_name}"

    return {
        "tracked_url": qr_result["tracked_url"],
        "qr_png": qr_result["qr_file"],
        "pdfs": pdfs,
    }


def issue_token(role: str, user_id: Optional[int] = None, partner_id: Optional[int] = None) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)).isoformat()
    with db_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, role, partner_id, expires_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (token, user_id, role, partner_id, expires_at, now_iso()),
        )
    return token


def session_from_header(authorization: Optional[str]) -> sqlite3.Row:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    with db_conn() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token")
    if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired")
    return row


def require_admin(authorization: Optional[str] = Header(default=None)) -> sqlite3.Row:
    session = session_from_header(authorization)
    if session["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return session


def require_partner(authorization: Optional[str] = Header(default=None)) -> sqlite3.Row:
    session = session_from_header(authorization)
    if session["role"] != "partner":
        raise HTTPException(status_code=403, detail="Partner only")
    return session


ensure_schema()


@app.on_event("startup")
def startup() -> None:
    ensure_schema()


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/partners/register")
def register_partner(payload: PartnerRegister) -> Dict[str, Any]:
    mobile = clean_mobile(payload.mobile)
    partner_type = normalize_partner_type(payload.partner_type)
    ref_code = make_ref_code(mobile)
    pin_plain = mobile[-4:]
    pin_hash = hash_secret(pin_plain)

    with db_conn() as conn:
        existing = conn.execute("SELECT id FROM partners WHERE mobile = ?", (mobile,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Record already exists for this mobile")

        conn.execute(
            """
            INSERT INTO partners (partner_type, name, mobile, pin_hash, address, latitude, longitude, ref_code, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                partner_type,
                payload.name.strip(),
                mobile,
                pin_hash,
                payload.address.strip(),
                payload.latitude,
                payload.longitude,
                ref_code,
                now_iso(),
                now_iso(),
            ),
        )

    assets = generate_assets(ref_code)
    return {
        "ok": True,
        "partner": {
            "name": payload.name.strip(),
            "mobile": mobile,
            "partner_type": partner_type,
            "address": payload.address.strip(),
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "ref_code": ref_code,
            "default_pin": pin_plain,
        },
        "assets": assets,
        "note": "Default partner PIN is last 4 digits of mobile. Ask partner to change later.",
    }


@app.post("/api/auth/partner-login")
def partner_login(payload: PartnerLogin) -> Dict[str, Any]:
    mobile = clean_mobile(payload.mobile)
    with db_conn() as conn:
        partner = conn.execute(
            "SELECT id, name, mobile, ref_code, pin_hash, active FROM partners WHERE mobile = ?",
            (mobile,),
        ).fetchone()
    if not partner or partner["active"] != 1:
        raise HTTPException(status_code=401, detail="Invalid partner credentials")
    if partner["pin_hash"] != hash_secret(payload.pin):
        raise HTTPException(status_code=401, detail="Invalid partner credentials")

    token = issue_token("partner", partner_id=partner["id"])
    return {
        "ok": True,
        "token": token,
        "partner": {
            "id": partner["id"],
            "name": partner["name"],
            "mobile": partner["mobile"],
            "ref_code": partner["ref_code"],
        },
    }


@app.post("/api/auth/admin-login")
def admin_login(payload: AdminLogin) -> Dict[str, Any]:
    mobile = clean_mobile(payload.mobile)
    with db_conn() as conn:
        user = conn.execute(
            "SELECT id, role, mobile, name, password_hash FROM users WHERE mobile = ?",
            (mobile,),
        ).fetchone()
    if not user or user["role"] != "admin" or user["password_hash"] != hash_secret(payload.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = issue_token("admin", user_id=user["id"])
    return {
        "ok": True,
        "token": token,
        "admin": {"id": user["id"], "name": user["name"], "mobile": user["mobile"]},
    }


@app.post("/api/events/track")
def track_event(payload: EventTrack, request: Request, user_agent: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    ref_code = payload.ref_code.strip()
    fwd_for = request.headers.get("x-forwarded-for", "")
    ip_raw = fwd_for.split(",")[0].strip() if fwd_for else (request.client.host if request.client else None)
    ip_h = hash_ip(ip_raw)
    with db_conn() as conn:
        partner = conn.execute("SELECT id FROM partners WHERE ref_code = ?", (ref_code,)).fetchone()
        if not partner:
            raise HTTPException(status_code=404, detail="Unknown ref code")

        meta = {
            "user_agent": user_agent,
        }
        conn.execute(
            """
            INSERT INTO events (event_type, ref_code, lead_token, number, category, page, metadata, ip_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.event_type,
                ref_code,
                payload.lead_token,
                payload.number,
                payload.category,
                payload.page,
                json.dumps(meta),
                ip_h,
                now_iso(),
            ),
        )

        if payload.event_type == "whatsapp_click" and payload.lead_token:
            lead = conn.execute(
                "SELECT id FROM leads WHERE lead_token = ?",
                (payload.lead_token,),
            ).fetchone()
            if not lead:
                conn.execute(
                    """
                    INSERT INTO leads (lead_token, ref_code, partner_id, status, created_at, updated_at)
                    VALUES (?, ?, ?, 'new', ?, ?)
                    """,
                    (payload.lead_token, ref_code, partner["id"], now_iso(), now_iso()),
                )

    return {"ok": True}


@app.get("/api/partners/{ref_code}/assets")
def partner_assets(ref_code: str) -> Dict[str, Any]:
    with db_conn() as conn:
        partner = conn.execute(
            "SELECT id, ref_code FROM partners WHERE ref_code = ?",
            (ref_code,),
        ).fetchone()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    assets = generate_assets(ref_code)
    return {"ok": True, "assets": assets}


@app.get("/api/partners/me/stats")
def partner_stats(session: sqlite3.Row = Depends(require_partner)) -> Dict[str, Any]:
    with db_conn() as conn:
        partner = conn.execute("SELECT id, name, ref_code FROM partners WHERE id = ?", (session["partner_id"],)).fetchone()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")

        scans = conn.execute(
            "SELECT COUNT(*) AS c FROM events WHERE ref_code = ? AND event_type = 'scan'",
            (partner["ref_code"],),
        ).fetchone()["c"]
        wa_clicks = conn.execute(
            "SELECT COUNT(*) AS c FROM events WHERE ref_code = ? AND event_type = 'whatsapp_click'",
            (partner["ref_code"],),
        ).fetchone()["c"]
        won = conn.execute(
            "SELECT COUNT(*) AS c FROM leads WHERE ref_code = ? AND status = 'won'",
            (partner["ref_code"],),
        ).fetchone()["c"]

    return {
        "ok": True,
        "partner": {"id": partner["id"], "name": partner["name"], "ref_code": partner["ref_code"]},
        "stats": {
            "scans": scans,
            "whatsapp_clicks": wa_clicks,
            "won_sales": won,
            "scan_to_whatsapp_rate": round((wa_clicks / scans) * 100, 2) if scans else 0,
        },
    }


@app.get("/api/partners/me/leads")
def partner_my_leads(limit: int = Query(default=100, ge=1, le=500), session: sqlite3.Row = Depends(require_partner)) -> Dict[str, Any]:
    with db_conn() as conn:
        ref_row = conn.execute("SELECT ref_code FROM partners WHERE id = ?", (session["partner_id"],)).fetchone()
        if not ref_row:
            raise HTTPException(status_code=404, detail="Partner not found")
        rows = conn.execute(
            """
            SELECT lead_token, status, sale_amount, created_at, updated_at, closed_at
            FROM leads
            WHERE ref_code = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (ref_row["ref_code"], limit),
        ).fetchall()
    return {"ok": True, "leads": [dict(r) for r in rows]}


@app.post("/api/partners/me/change-pin")
def partner_change_pin(payload: PartnerPinChange, session: sqlite3.Row = Depends(require_partner)) -> Dict[str, Any]:
    with db_conn() as conn:
        partner = conn.execute("SELECT id, pin_hash FROM partners WHERE id = ?", (session["partner_id"],)).fetchone()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        if partner["pin_hash"] != hash_secret(payload.current_pin):
            raise HTTPException(status_code=401, detail="Current PIN is incorrect")
        conn.execute(
            "UPDATE partners SET pin_hash = ?, updated_at = ? WHERE id = ?",
            (hash_secret(payload.new_pin), now_iso(), partner["id"]),
        )
    return {"ok": True}


@app.get("/api/admin/partners")
def admin_list_partners(
    q: str = Query(default=""),
    active: Optional[bool] = Query(default=None),
    session: sqlite3.Row = Depends(require_admin),
) -> Dict[str, Any]:
    where = []
    params: list[Any] = []
    if q.strip():
        where.append("(name LIKE ? OR mobile LIKE ? OR ref_code LIKE ? OR address LIKE ?)")
        s = f"%{q.strip()}%"
        params.extend([s, s, s, s])
    if active is not None:
        where.append("active = ?")
        params.append(1 if active else 0)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with db_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, name, mobile, partner_type, address, latitude, longitude, ref_code, active, created_at, updated_at
            FROM partners
            {where_sql}
            ORDER BY created_at DESC
            LIMIT 2000
            """,
            tuple(params),
        ).fetchall()
    return {"ok": True, "partners": [dict(r) for r in rows]}


@app.patch("/api/admin/partners/{partner_id}")
def admin_update_partner(partner_id: int, payload: AdminPartnerUpdate, session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    fields = []
    values: list[Any] = []

    if payload.name is not None:
        fields.append("name = ?")
        values.append(payload.name.strip())
    if payload.address is not None:
        fields.append("address = ?")
        values.append(payload.address.strip())
    if payload.latitude is not None:
        fields.append("latitude = ?")
        values.append(payload.latitude)
    if payload.longitude is not None:
        fields.append("longitude = ?")
        values.append(payload.longitude)
    if payload.partner_type is not None:
        fields.append("partner_type = ?")
        values.append(normalize_partner_type(payload.partner_type))
    if payload.active is not None:
        fields.append("active = ?")
        values.append(1 if payload.active else 0)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided")

    fields.append("updated_at = ?")
    values.append(now_iso())
    values.append(partner_id)

    with db_conn() as conn:
        row = conn.execute("SELECT id FROM partners WHERE id = ?", (partner_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Partner not found")
        conn.execute(f"UPDATE partners SET {', '.join(fields)} WHERE id = ?", tuple(values))
    return {"ok": True}


@app.post("/api/admin/partners/{partner_id}/reset-pin")
def admin_reset_partner_pin(partner_id: int, payload: AdminPartnerPinReset, session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    with db_conn() as conn:
        row = conn.execute("SELECT id FROM partners WHERE id = ?", (partner_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Partner not found")
        conn.execute(
            "UPDATE partners SET pin_hash = ?, updated_at = ? WHERE id = ?",
            (hash_secret(payload.new_pin), now_iso(), partner_id),
        )
    return {"ok": True}


@app.post("/api/partners/{ref_code}/custom-pdf")
def partner_custom_pdf(ref_code: str, payload: CustomPdfRequest, session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    with db_conn() as conn:
        partner = conn.execute("SELECT id FROM partners WHERE ref_code = ?", (ref_code,)).fetchone()
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
    qr_result = create_qr(ref_code)
    qr_file_path = GENERATED_DIR / f"{ref_code}.png"
    safe_label = "".join(ch for ch in payload.label.lower().strip().replace(" ", "-") if ch.isalnum() or ch in {"-", "_"})
    if not safe_label:
        safe_label = "custom"
    pdf_name = f"{ref_code}-{safe_label}-{int(payload.width_in)}x{int(payload.height_in)}.pdf"
    pdf_path = GENERATED_DIR / pdf_name
    draw_partner_pdf(pdf_path, ref_code, qr_file_path, (payload.width_in * inch, payload.height_in * inch), payload.label)
    return {"ok": True, "tracked_url": qr_result["tracked_url"], "pdf": f"/generated/{pdf_name}"}


@app.get("/api/admin/overview")
def admin_overview(session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    with db_conn() as conn:
        totals = {
            "partners": conn.execute("SELECT COUNT(*) AS c FROM partners").fetchone()["c"],
            "scans": conn.execute("SELECT COUNT(*) AS c FROM events WHERE event_type = 'scan'").fetchone()["c"],
            "whatsapp_clicks": conn.execute("SELECT COUNT(*) AS c FROM events WHERE event_type = 'whatsapp_click'").fetchone()["c"],
            "won_sales": conn.execute("SELECT COUNT(*) AS c FROM leads WHERE status = 'won'").fetchone()["c"],
        }
        top = conn.execute(
            """
            SELECT p.name, p.ref_code,
                   SUM(CASE WHEN e.event_type='scan' THEN 1 ELSE 0 END) AS scans,
                   SUM(CASE WHEN e.event_type='whatsapp_click' THEN 1 ELSE 0 END) AS wa_clicks
            FROM partners p
            LEFT JOIN events e ON e.ref_code = p.ref_code
            GROUP BY p.id
            ORDER BY wa_clicks DESC, scans DESC
            LIMIT 10
            """
        ).fetchall()

    return {
        "ok": True,
        "totals": totals,
        "top_agents": [dict(row) for row in top],
    }


@app.get("/api/admin/leads")
def admin_list_leads(session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT l.lead_token, l.ref_code, l.status, l.sale_amount, l.created_at, l.updated_at, p.name AS partner_name, p.mobile
            FROM leads l
            LEFT JOIN partners p ON p.id = l.partner_id
            ORDER BY l.created_at DESC
            LIMIT 500
            """
        ).fetchall()
    return {"ok": True, "leads": [dict(r) for r in rows]}


@app.post("/api/leads/{lead_token}/status")
def admin_update_lead(lead_token: str, payload: LeadUpdate, session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    closed_at = now_iso() if payload.status in {"won", "lost"} else None
    with db_conn() as conn:
        lead = conn.execute("SELECT id FROM leads WHERE lead_token = ?", (lead_token,)).fetchone()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        conn.execute(
            """
            UPDATE leads
            SET status = ?, sale_amount = ?, updated_at = ?, closed_at = ?
            WHERE lead_token = ?
            """,
            (payload.status, payload.sale_amount, now_iso(), closed_at, lead_token),
        )
    return {"ok": True}


@app.get("/api/admin/analytics/daily")
def admin_daily_analytics(days: int = Query(default=30, ge=1, le=365), session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT substr(created_at, 1, 10) AS day,
                   SUM(CASE WHEN event_type='scan' THEN 1 ELSE 0 END) AS scans,
                   SUM(CASE WHEN event_type='whatsapp_click' THEN 1 ELSE 0 END) AS whatsapp_clicks
            FROM events
            WHERE datetime(created_at) >= datetime('now', ?)
            GROUP BY day
            ORDER BY day DESC
            """,
            (f"-{days} days",),
        ).fetchall()
    return {"ok": True, "days": days, "series": [dict(r) for r in rows]}


@app.get("/api/admin/analytics/city")
def admin_city_analytics(session: sqlite3.Row = Depends(require_admin)) -> Dict[str, Any]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT lower(trim(substr(p.address, instr(p.address, ',') + 1))) AS city,
                   SUM(CASE WHEN e.event_type='scan' THEN 1 ELSE 0 END) AS scans,
                   SUM(CASE WHEN e.event_type='whatsapp_click' THEN 1 ELSE 0 END) AS whatsapp_clicks
            FROM partners p
            LEFT JOIN events e ON e.ref_code = p.ref_code
            GROUP BY city
            ORDER BY scans DESC, whatsapp_clicks DESC
            """
        ).fetchall()
    normalized = []
    for r in rows:
        city = (r["city"] or "").strip() or "unknown"
        normalized.append({"city": city, "scans": r["scans"] or 0, "whatsapp_clicks": r["whatsapp_clicks"] or 0})
    return {"ok": True, "cities": normalized}


def _csv_response(filename: str, rows: list[dict], fieldnames: list[str]) -> Response:
    stream = io.StringIO()
    writer = DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    content = stream.getvalue()
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=content, media_type="text/csv", headers=headers)


@app.get("/api/admin/export/leads.csv")
def export_leads_csv(session: sqlite3.Row = Depends(require_admin)) -> Response:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT l.lead_token, l.ref_code, p.name AS partner_name, p.mobile AS partner_mobile,
                   l.status, l.sale_amount, l.created_at, l.updated_at, l.closed_at
            FROM leads l
            LEFT JOIN partners p ON p.id = l.partner_id
            ORDER BY l.created_at DESC
            """
        ).fetchall()
    data = [dict(r) for r in rows]
    fields = ["lead_token", "ref_code", "partner_name", "partner_mobile", "status", "sale_amount", "created_at", "updated_at", "closed_at"]
    return _csv_response("leads_export.csv", data, fields)


@app.get("/api/admin/export/partners.csv")
def export_partners_csv(session: sqlite3.Row = Depends(require_admin)) -> Response:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, partner_type, name, mobile, address, latitude, longitude, ref_code, active, created_at, updated_at
            FROM partners
            ORDER BY created_at DESC
            """
        ).fetchall()
    data = [dict(r) for r in rows]
    fields = ["id", "partner_type", "name", "mobile", "address", "latitude", "longitude", "ref_code", "active", "created_at", "updated_at"]
    return _csv_response("partners_export.csv", data, fields)
