# Retell AI Webhook Integration — Status & Next Steps

**Last Updated:** October 6, 2026
**Test Suite:** 76/76 passing

---

## Current Cloudflare Tunnel

```
Public URL:  use the current URL printed by cloudflared
Local URL:   http://localhost:8000
```

Quick tunnels change URL when restarted. Do not reuse a previous URL unless the tunnel is still running.

---

## What's Working ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Book-appointment endpoint | ✅ Working | `POST /api/webhooks/retell/book-appointment` |
| Backend date normalizer | ✅ Working | Auto-corrects past years to next future occurrence |
| Lead creation | ✅ Working | Created from customer_name + customer_phone |
| Call creation (synthetic) | ✅ Working | Created by book-appointment endpoint |
| Appointment creation | ✅ Working | Linked to Lead + Call |
| FK relationships | ✅ Working | Lead → Call → Appointment all valid |
| Activity logging | ✅ Working | appointment_booked activity created |
| Dashboard KPIs | ✅ Working | Calculated from real DB records |
| Frontend API endpoints | ✅ Working | All CRUD endpoints functional |
| Test suite | ✅ 76/76 passing | Full coverage of webhook pipeline |

### Retell URL Configuration

Configure these URLs separately in Retell:

- **BookAppointment custom function URL:** `https://<current-tunnel-host>/api/webhooks/retell/book-appointment`
- **Agent-level lifecycle webhook URL:** `https://<current-tunnel-host>/api/webhooks/retell`

The booking function accepts `BookAppointment`, `book_appointment`, and equivalent casing on the general lifecycle URL as well. Use the dedicated booking URL for the custom function so booking errors are returned directly and lifecycle events remain separate.

---

## Manual Retell Setup And Test

The local code cannot confirm which URLs or prompt variables are currently saved in your Retell account. Before the final live test:

1. Keep the backend running at `http://localhost:8000` and start cloudflared with `cloudflared tunnel --url http://localhost:8000`.
2. Copy the current public tunnel URL printed by cloudflared.
3. In **Retell → Agent → Custom Functions**, set the booking function URL to `<PUBLIC_TUNNEL_URL>/api/webhooks/retell/book-appointment`.
4. In **Retell → Agent → Webhook URL**, set the agent-level lifecycle URL to `<PUBLIC_TUNNEL_URL>/api/webhooks/retell`.
5. For the booking function, send customer name, phone, and appointment date/time. Prefer `customer_name`, `customer_phone`, and ISO `start_time` (for example `2026-10-08T10:00:00`). The handler also accepts common aliases and PascalCase function names such as `BookAppointment`.
6. Check the prompt's `{{current_date}}` placeholder. If Retell does not replace it with the current date, use Retell's supported dynamic variable or update the literal date before testing.
7. Make a real call, then confirm the appointment appears in the dashboard's Upcoming Appointments and Appointments pages. The dashboard websocket should show **Live** and refresh after a booking.

The booking endpoint can create the appointment independently. Lifecycle webhooks add the provider call ID, duration, transcript, and analysis when Retell sends those events. A successful ping from Retell's webhook test button does not prove that real call lifecycle events are configured.

---

## Architecture Recap

```
Retell AI Agent (cloud)
  ├── Custom Function: book-appointment
  │     → POST /api/webhooks/retell/book-appointment ✅ WORKS
  │     → Creates: Lead + synthetic Call + Appointment
  │
  └── Agent-level lifecycle webhook
     → POST /api/webhooks/retell
     → Updates call data + lead + transcript
```

The booking endpoint, casing normalization, dashboard refresh event, and frontend websocket proxy are covered by local tests. Live Retell delivery still needs the manual account configuration above.

## Current Fixes

| File | Change |
|------|--------|
| `backend/app/api/webhooks.py` | Normalize Retell function-name casing and broadcast booking refreshes |
| `backend/tests/test_webhooks.py` | Cover PascalCase booking calls on the general webhook |
| `backend/tests/test_dashboard.py` | Verify booked appointments appear in dashboard data |
| `frontend/vite.config.js` | Proxy `/ws` to FastAPI so dashboard realtime updates connect |
| `frontend/src/App.jsx` | Lazy-load routes to reduce initial bundle size |
| `frontend/src/components/Layout.jsx`, `frontend/src/pages/`, `frontend/src/index.css` | Refresh the shared navigation, dashboard, login, and application theme |

---

## Retell Prompt Notes

The improved prompt is saved in `retell_agent_prompt.md` at the project root. Key additions:
- `{{current_date}}` dynamic variable (may not work in all Retell plans)
- Explicit date examples using 2026
- Instructions to never use 2024
- Natural conversation flow improvements

---

## Test Suite

```bash
cd backend && python -m pytest tests/ -v
```

Expected: **76 passed, 0 failed**
