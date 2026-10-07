# VoiceFlow AI — AI Voice Sales & Receptionist Automation Platform

A complete AI Voice Sales & Receptionist system for businesses. Handles inbound AI receptionist calls, outbound sales calling, lead qualification, appointment booking, call summaries, CRM management, and real-time analytics.

Built as a portfolio product demonstrating AI voice automation capabilities for Fiverr clients.

---

## 🎯 What It Does

| Capability | Description |
|---|---|
| **AI Voice Receptionist** | Answers inbound calls, collects info, qualifies leads |
| **Outbound Sales Agent** | Calls leads, handles objections, books appointments |
| **Lead Qualification** | Scores leads (0-100), assigns temperature (cold/warm/hot) |
| **Appointment Booking** | Schedules, confirms, and manages appointments |
| **Call Tracking** | Full call records with transcripts and summaries |
| **AI Call Summaries** | Structured summaries with intent, score, and next actions |
| **CRM / Lead Management** | Professional CRM-style lead pipeline |
| **Campaign Management** | Outbound calling campaigns with metrics |
| **Analytics Dashboard** | Real-time KPIs, charts, and performance metrics |
| **Webhook Integration** | Retell AI and Vapi AI webhook processing |
| **Follow-up System** | Automated follow-up scheduling |
| **Activity Logging** | Complete audit trail of all system events |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│          React + Vite + Tailwind CSS             │
│  Dashboard │ Calls │ Leads │ Appointments │ ...  │
└──────────────────────┬──────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────┐
│                   Backend                        │
│              FastAPI + SQLAlchemy                │
│  API Layer → Service Layer → Database            │
└──────────────────────┬──────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐  ┌───────────┐  ┌──────────┐
   │ SQLite  │  │ Retell AI │  │  Vapi AI │
   │   DB    │  │ Webhooks  │  │ Webhooks │
   └─────────┘  └───────────┘  └──────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Google Calendar  Google Sheets   CRM/SMS/Email
   (optional)       (optional)      (optional)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Pydantic |
| Frontend | React 19, Vite, Tailwind CSS 4, Recharts |
| Database | SQLite (MVP) — easily swap to PostgreSQL |
| Auth | JWT tokens, bcrypt password hashing |
| Integrations | Retell AI, Vapi AI, Google Calendar/Sheets |
| Testing | pytest, httpx TestClient |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Start the backend:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
Swagger docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

### Login

Use the demo credentials:
- **Email:** admin@voiceflow.ai
- **Password:** admin123

### Generate Demo Data

After logging in, click **"Generate Demo Data"** on the dashboard (or use `POST /api/demo/seed`).

This creates:
- 12 realistic leads
- 20 calls with transcripts
- 5 appointments
- 1 campaign
- 4 follow-ups
- 20 activity log entries

---

## 📊 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login, get JWT token |
| GET | `/api/auth/me` | Get current user |

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard` | Full dashboard data (KPIs, charts, activity) |

### Leads
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/leads` | List leads (filterable) |
| POST | `/api/leads` | Create lead |
| GET | `/api/leads/{id}` | Get lead |
| PUT | `/api/leads/{id}` | Update lead |
| DELETE | `/api/leads/{id}` | Delete lead |

### Calls
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/calls` | List calls (filterable) |
| POST | `/api/calls` | Create call |
| GET | `/api/calls/{id}` | Get call details |
| PUT | `/api/calls/{id}` | Update call |

### Appointments
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/appointments` | List appointments |
| POST | `/api/appointments` | Create appointment |
| PUT | `/api/appointments/{id}` | Update appointment |
| DELETE | `/api/appointments/{id}` | Cancel appointment |

### Campaigns
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Create campaign |
| GET | `/api/campaigns/{id}` | Get campaign |
| PUT | `/api/campaigns/{id}` | Update campaign |
| POST | `/api/campaigns/{id}/leads` | Add leads to campaign |

### Webhooks
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/webhooks/retell` | Retell AI webhook receiver |
| POST | `/api/webhooks/vapi` | Vapi AI webhook receiver |

### Other
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/activity` | Activity log |
| GET | `/api/settings` | App settings/status |
| POST | `/api/demo/seed` | Generate demo data |

---

## 🔧 Environment Variables

Copy `backend/.env.example` to `backend/.env`:

```env
APP_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./voiceflow.db

# Optional — leave empty for demo mode
RETELL_API_KEY=
VAPI_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
OPENAI_API_KEY=
```

All external integrations are optional. The app runs fully in demo mode without any API keys.

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v
```

36 tests covering:
- Authentication (login, JWT, protected routes)
- Lead CRUD and qualification scoring
- Call CRUD and status updates
- Appointment management
- Dashboard KPI calculations
- Webhook processing (Retell & Vapi)
- Duplicate webhook protection
- Demo data seeding

---

## 🔌 Integration Setup

### Retell AI

1. Get API key from [retellai.com](https://retellai.com)
2. Add to `.env`:
   ```
   RETELL_API_KEY=your_key_here
   RETELL_AGENT_ID=your_agent_id
   ```
3. Configure Retell webhook URL: `https://your-domain.com/api/webhooks/retell`

### Vapi AI

1. Get API key from [vapi.ai](https://vapi.ai)
2. Add to `.env`:
   ```
   VAPI_API_KEY=your_key_here
   VAPI_ASSISTANT_ID=your_assistant_id
   ```
3. Configure Vapi webhook URL: `https://your-domain.com/api/webhooks/vapi`

### Google Calendar

1. Create Google Cloud project with Calendar API enabled
2. Add credentials to `.env`:
   ```
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   GOOGLE_CALENDAR_ID=your_calendar_id
   ```

---

## 🐳 Docker

```bash
docker-compose up
```

Or build individually:

```bash
cd backend && docker build -t voiceflow-backend .
cd frontend && docker build -t voiceflow-frontend .
```

---

## 📁 Project Structure

```
voiceflow-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/                 # Config, security, logging
│   │   ├── database/             # SQLAlchemy setup
│   │   ├── models/               # Database models (8 tables)
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── api/                  # REST API endpoints (10 routers)
│   │   ├── services/             # Business logic layer (7 services)
│   │   ├── integrations/         # Provider abstractions (8 modules)
│   │   ├── utils/                # Helpers and validators
│   │   └── demo/                 # Demo data seeding
│   ├── tests/                    # 36 automated tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Routes
│   │   ├── pages/                # 10 page components
│   │   ├── components/           # Layout, StatusBadge
│   │   ├── context/              # Auth context
│   │   └── services/             # API client
│   └── package.json
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 🎯 Target Industries

This platform is designed to be customized for:
- Real estate agencies
- Dental/medical clinics
- Home service businesses (roofing, plumbing, HVAC)
- Law firms
- Insurance agencies
- Marketing agencies
- SaaS companies
- Local businesses

---

## 📝 License

Private — Built as a portfolio product.
