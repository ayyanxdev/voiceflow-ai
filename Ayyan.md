# VoiceFlow AI Presentation Runbook

Use five PowerShell terminals and keep the backend, tunnel, and frontend terminals open during the demo. Run backend commands from the `backend` folder so the app uses `backend/voiceflow.db`.

## 1. Start the backend

In PowerShell terminal 1:

```powershell
Set-Location 'B:\AI Automation\month 4\backend'
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Wait for `Application startup complete`. Check the local API at `http://127.0.0.1:8000/health` and docs at `http://127.0.0.1:8000/docs`.

## 2. Start the Cloudflare tunnel

In PowerShell terminal 2:

```powershell
& 'C:\Program Files (x86)\cloudflared\cloudflared.exe' tunnel --url http://127.0.0.1:8000
```

Keep this terminal open. Copy the current `https://...trycloudflare.com` URL from its output. The URL can change whenever the quick tunnel restarts. The current URL recorded for this setup is:

```text
https://absolutely-wifi-wearing-protected.trycloudflare.com
```

Verify that `<TUNNEL_URL>/health` returns `{"status":"healthy"}` before testing Retell.

## 3. Configure the Retell agent and booking function

In the Retell agent settings, use the current tunnel URL for both endpoints:

- Agent-level Webhook URL: `<TUNNEL_URL>/api/webhooks/retell`
- `BookAppointment` custom function URL: `<TUNNEL_URL>/api/webhooks/retell/book-appointment`

For the custom function, select **JSON** and set **Payload: args only** to **OFF**. This sends Retell's normal envelope (`name`, `args`, and `call`), which also lets the backend use transcript fallback if needed.

Create these parameters. The address goes in `notes`; the backend also accepts `address` as an alias.

| Parameter Name | Detail / Description | Type | Required |
|---|---|---|---|
| `customer_name` | Full name of the customer | String | Yes |
| `customer_phone` | Customer phone number | String | Yes |
| `start_time` | Appointment start time in ISO 8601, e.g. `2026-10-07T18:00:00` | String | Yes |
| `title` | Appointment title or reason | String | No |
| `customer_email` | Customer email | String | No |
| `end_time` | Appointment end time in ISO 8601 | String | No |
| `notes` | Free-text notes; include the service address here | String | No |
| `lead_id` | Existing lead ID to link | Integer | No |
| `call_id` | Existing database call ID to link | Integer | No |
| `business_id` | Business ID | Integer | No |

The three required fields should be sent as populated arguments. The transcript fallback is only a safety net for a misconfigured function.

## 4. Start the frontend and sign in

In PowerShell terminal 3:

```powershell
Set-Location 'B:\AI Automation\month 4\frontend'
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`. Demo login:

```text
Email: admin@voiceflow.ai
Password: admin123
```

## 5. Run and verify the live booking demo

Make a real call to the Retell number. Give a name, phone number, Lahore/service address, and a future appointment time within the business hours configured in the agent prompt. Confirm the date and time verbally, then approve the booking.

Expected result: Retell reports the booking succeeded; the dashboard shows **Live**; the appointment appears under **Upcoming Appointments** and on the **Appointments** page. Uvicorn should log the booking and return an `appointment_id`. Do not click **Generate Demo Data** unless you want sample records in the presentation.

If the tunnel URL changes, update both Retell URLs in step 3 before the call. Do not run the database clear endpoint during presentation setup; it deletes leads, calls, appointments, activities, and businesses.
