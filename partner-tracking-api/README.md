# Partner Tracking API (Phase 1 MVP)

This service adds:
- Partner onboarding with unique mobile enforcement
- Auto-generated partner `ref_code`
- QR + print PDF generation (`4x6`, `A4`, `square`)
- Custom size PDF generation
- Scan + WhatsApp click event tracking
- Lead token creation flow for WhatsApp attribution
- Admin + partner dashboards via API
- Partner management (activate/deactivate, type/name update, PIN reset)
- Daily + city analytics and CSV exports

## Run

```powershell
cd C:\Users\Malik\desktop\etisalat-shop\partner-tracking-api
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8003
```

Open docs:
- `http://127.0.0.1:8003/docs`

Generated files:
- `partner-tracking-api/generated/*.png`
- `partner-tracking-api/generated/*.pdf`

## Environment

Copy `.env.example` to `.env` and set values.

Important:
- `ADMIN_PASSWORD` must be changed before production.
- `APP_SALT` must be random and private.

## UI Pages

Static UI pages are in:
- `partner-portal/onboard.html`
- `partner-portal/admin.html`
- `partner-portal/partner-dashboard.html`
- `partner-portal/qr-style-mockups.html`

Set API base URL in each page (default `http://127.0.0.1:8003`).

## Attribution window

`choose-number/index.html` stores partner `ref` for **90 days** in local storage.
Each WhatsApp click appends:
- `Ref:<ref_code>`
- `LeadToken:<generated_token>`

This allows commission mapping in exported chat history.

## Key API routes

- `POST /api/partners/register`
- `POST /api/auth/admin-login`
- `POST /api/auth/partner-login`
- `POST /api/events/track`
- `GET /api/partners/{ref_code}/assets`
- `POST /api/partners/{ref_code}/custom-pdf` (admin token required)
- `GET /api/partners/me/stats`
- `GET /api/partners/me/leads`
- `POST /api/partners/me/change-pin`
- `GET /api/admin/overview`
- `GET /api/admin/analytics/daily`
- `GET /api/admin/analytics/city`
- `GET /api/admin/partners`
- `PATCH /api/admin/partners/{partner_id}`
- `POST /api/admin/partners/{partner_id}/reset-pin`
- `GET /api/admin/leads`
- `POST /api/leads/{lead_token}/status`
- `GET /api/admin/export/leads.csv`
- `GET /api/admin/export/partners.csv`
