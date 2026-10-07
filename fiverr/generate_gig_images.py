"""Generate professional Fiverr gig images using HTML + Chrome headless screenshots."""

import subprocess
import os
import json
import urllib.request
import time

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BACKEND = "http://localhost:8000"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "gig_images")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def get_token():
    data = json.dumps({"email": "admin@voiceflow.ai", "password": "admin123"}).encode()
    req = urllib.request.Request(
        f"{BACKEND}/api/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["access_token"]


def get_dashboard(token):
    req = urllib.request.Request(
        f"{BACKEND}/api/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def get_leads(token):
    req = urllib.request.Request(
        f"{BACKEND}/api/leads",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    return data if isinstance(data, list) else data.get("items", data.get("leads", []))


def get_calls(token):
    req = urllib.request.Request(
        f"{BACKEND}/api/calls",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    return data if isinstance(data, list) else data.get("items", data.get("calls", []))


def get_appointments(token):
    req = urllib.request.Request(
        f"{BACKEND}/api/appointments",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    return data if isinstance(data, list) else data.get("items", data.get("appointments", []))


def screenshot_html(html_content, output_path, width=1280, height=720):
    """Write HTML to temp file and screenshot it."""
    tmp_html = os.path.join(SCREENSHOT_DIR, "_tmp.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_url = "file:///" + os.path.abspath(tmp_html).replace("\\", "/")
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={width},{height}",
        f"--screenshot={output_path}",
        "--hide-scrollbars",
        "--virtual-time-budget=3000",
        file_url,
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"  ✓ {os.path.basename(output_path)} ({size:,} bytes)")
    else:
        print(f"  ✗ Failed: {os.path.basename(output_path)}")
    # Cleanup
    if os.path.exists(tmp_html):
        os.remove(tmp_html)


# ── GIG IMAGE 1: MAIN THUMBNAIL ─────────────────────────────────────
def create_main_thumbnail(dashboard):
    ov = dashboard["overview"]
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: 1280px; height: 720px;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 40%, #0d1117 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    display: flex; overflow: hidden; color: white;
}}
.left {{
    width: 55%; padding: 48px 40px;
    display: flex; flex-direction: column; justify-content: center;
}}
.badge {{
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
    padding: 6px 16px; border-radius: 20px; font-size: 13px; color: #a5b4fc;
    margin-bottom: 24px; width: fit-content;
}}
.badge .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #22c55e; }}
h1 {{
    font-size: 48px; font-weight: 800; line-height: 1.1;
    background: linear-gradient(135deg, #fff 0%, #c7d2fe 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
}}
.subtitle {{ font-size: 18px; color: #94a3b8; line-height: 1.5; margin-bottom: 32px; }}
.features {{
    display: flex; flex-direction: column; gap: 12px;
}}
.feature {{
    display: flex; align-items: center; gap: 12px;
    font-size: 15px; color: #cbd5e1;
}}
.feature .icon {{
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}}
.feature .icon.blue {{ background: rgba(59,130,246,0.2); }}
.feature .icon.green {{ background: rgba(34,197,94,0.2); }}
.feature .icon.purple {{ background: rgba(139,92,246,0.2); }}
.feature .icon.amber {{ background: rgba(245,158,11,0.2); }}

.right {{
    width: 45%; padding: 40px 40px 40px 0;
    display: flex; align-items: center; justify-content: center;
}}
.dashboard-mock {{
    width: 100%; max-width: 520px;
    background: #161b22; border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 25px 60px rgba(0,0,0,0.5);
    overflow: hidden;
}}
.dash-header {{
    padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; justify-content: space-between;
}}
.dash-header h3 {{ font-size: 14px; color: #e2e8f0; font-weight: 600; }}
.dash-header .live {{ font-size: 11px; color: #22c55e; }}
.kpi-row {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
    padding: 16px 20px;
}}
.kpi {{
    background: rgba(255,255,255,0.04); border-radius: 10px;
    padding: 12px; text-align: center;
}}
.kpi .value {{ font-size: 22px; font-weight: 700; }}
.kpi .label {{ font-size: 10px; color: #64748b; margin-top: 4px; }}
.kpi.violet .value {{ color: #8b5cf6; }}
.kpi.blue .value {{ color: #3b82f6; }}
.kpi.green .value {{ color: #22c55e; }}
.kpi.amber .value {{ color: #f59e0b; }}
.chart-area {{
    padding: 16px 20px; border-top: 1px solid rgba(255,255,255,0.06);
}}
.chart-label {{ font-size: 12px; color: #94a3b8; margin-bottom: 8px; }}
.chart-bars {{
    display: flex; align-items: flex-end; gap: 6px; height: 80px;
}}
.chart-bar {{
    flex: 1; border-radius: 4px 4px 0 0; min-height: 8px;
}}
.calls-row {{
    display: flex; flex-direction: column; gap: 6px;
    padding: 12px 20px; border-top: 1px solid rgba(255,255,255,0.06);
}}
.call-item {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 12px; background: rgba(255,255,255,0.03);
    border-radius: 8px; font-size: 12px;
}}
.call-item .name {{ color: #e2e8f0; font-weight: 500; }}
.call-item .meta {{ color: #64748b; }}
.call-item .status {{
    padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600;
}}
.call-item .status.qualified {{ background: rgba(34,197,94,0.15); color: #22c55e; }}
.call-item .status.booked {{ background: rgba(139,92,246,0.15); color: #a78bfa; }}
</style></head><body>
<div class="left">
    <div class="badge"><span class="dot"></span> AI-Powered Voice Platform</div>
    <h1>AI Receptionist<br>for Your Business</h1>
    <p class="subtitle">24/7 automated call handling, lead qualification,<br>and appointment booking — with a full dashboard.</p>
    <div class="features">
        <div class="feature"><div class="icon blue">📞</div> Answers calls with natural AI voice</div>
        <div class="feature"><div class="icon green">📊</div> Lead scoring & management dashboard</div>
        <div class="feature"><div class="icon purple">📅</div> Automatic appointment booking</div>
        <div class="feature"><div class="icon amber">📈</div> Real-time analytics & call summaries</div>
    </div>
</div>
<div class="right">
    <div class="dashboard-mock">
        <div class="dash-header">
            <h3>Dashboard</h3>
            <span class="live">● Live</span>
        </div>
        <div class="kpi-row">
            <div class="kpi violet"><div class="value">{ov['total_calls']}</div><div class="label">Total Calls</div></div>
            <div class="kpi blue"><div class="value">{ov['answered_calls']}</div><div class="label">Answered</div></div>
            <div class="kpi green"><div class="value">{ov['qualified_leads']}</div><div class="label">Qualified</div></div>
            <div class="kpi amber"><div class="value">{ov['appointments_booked']}</div><div class="label">Booked</div></div>
        </div>
        <div class="chart-area">
            <div class="chart-label">Calls Over Time</div>
            <div class="chart-bars">
                <div class="chart-bar" style="height:40%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:65%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:50%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:80%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:70%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:90%; background:#818cf8;"></div>
                <div class="chart-bar" style="height:55%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:75%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:85%; background:#6366f1;"></div>
                <div class="chart-bar" style="height:60%; background:#6366f1;"></div>
            </div>
        </div>
        <div class="calls-row">
            <div class="call-item">
                <span class="name">John Smith</span>
                <span class="meta">Inbound · 3:24</span>
                <span class="status qualified">Qualified</span>
            </div>
            <div class="call-item">
                <span class="name">Sarah Johnson</span>
                <span class="meta">Inbound · 2:15</span>
                <span class="status booked">Booked</span>
            </div>
        </div>
    </div>
</div>
</body></html>"""
    screenshot_html(html, os.path.join(SCREENSHOT_DIR, "01_main_thumbnail.png"))


# ── GIG IMAGE 2: LEAD MANAGEMENT KANBAN ──────────────────────────────
def create_lead_management(leads):
    # Get some sample leads
    sample = leads[:8] if len(leads) >= 8 else leads
    kanban_cols = {
        "New": [l for l in sample if l.get("status") == "new"][:3],
        "Contacted": [l for l in sample if l.get("status") == "contacted"][:3],
        "Qualified": [l for l in sample if l.get("status") == "qualified"][:3],
        "Appointment": [l for l in sample if l.get("status") == "appointment_booked"][:3],
    }
    
    def lead_card(name, phone, score, temp):
        flame = "🔥" if temp == "hot" else "🌤" if temp == "warm" else "❄️"
        score_color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 40 else "#64748b"
        return f"""<div class="lead-card">
            <div class="lead-top">
                <div class="avatar">{name[0] if name else '?'}</div>
                <div><div class="lead-name">{name}</div><div class="lead-phone">{phone or ''}</div></div>
            </div>
            <div class="lead-bottom">
                <span class="temp">{flame} {temp}</span>
                <span class="score" style="color:{score_color}">{score}</span>
            </div>
        </div>"""
    
    columns_html = ""
    colors = {"New": "#3b82f6", "Contacted": "#f59e0b", "Qualified": "#10b981", "Appointment": "#6366f1"}
    for col_name, col_leads in kanban_cols.items():
        cards = "".join(
            lead_card(
                f"{l.get('first_name', '')} {l.get('last_name', '')}".strip(),
                l.get("phone", ""),
                l.get("qualification_score", 0),
                l.get("temperature", "cold"),
            )
            for l in col_leads
        )
        if not col_leads:
            cards = '<div class="empty">No leads</div>'
        columns_html += f"""<div class="kanban-col">
            <div class="col-header" style="border-top: 3px solid {colors[col_name]}">
                <span class="col-dot" style="background:{colors[col_name]}"></span>
                <span>{col_name}</span>
                <span class="col-count">{len(col_leads)}</span>
            </div>
            <div class="col-cards">{cards}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: 1280px; height: 720px;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 40%, #0d1117 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    padding: 40px; color: white; overflow: hidden;
}}
.header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px;
}}
.header h2 {{
    font-size: 28px; font-weight: 700;
    background: linear-gradient(135deg, #fff, #c7d2fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.header .stats {{
    display: flex; gap: 20px;
}}
.stat {{ text-align: center; }}
.stat .val {{ font-size: 24px; font-weight: 700; color: #8b5cf6; }}
.stat .lbl {{ font-size: 11px; color: #64748b; }}
.kanban {{ display: flex; gap: 16px; height: 560px; }}
.kanban-col {{
    flex: 1; background: rgba(255,255,255,0.03);
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
    display: flex; flex-direction: column; overflow: hidden;
}}
.col-header {{
    padding: 12px 16px; display: flex; align-items: center; gap: 8px;
    font-size: 13px; font-weight: 600; color: #e2e8f0;
    background: rgba(255,255,255,0.02);
}}
.col-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
.col-count {{
    margin-left: auto; background: rgba(255,255,255,0.06);
    padding: 2px 8px; border-radius: 10px; font-size: 11px; color: #94a3b8;
}}
.col-cards {{ padding: 8px; display: flex; flex-direction: column; gap: 8px; flex: 1; overflow: hidden; }}
.lead-card {{
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 12px; cursor: pointer;
}}
.lead-top {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
.avatar {{
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg, #8b5cf6, #3b82f6);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; color: white; flex-shrink: 0;
}}
.lead-name {{ font-size: 13px; font-weight: 600; color: #e2e8f0; }}
.lead-phone {{ font-size: 11px; color: #64748b; }}
.lead-bottom {{
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06);
}}
.temp {{ font-size: 11px; color: #94a3b8; }}
.score {{ font-size: 13px; font-weight: 700; }}
.empty {{ text-align: center; color: #475569; font-size: 12px; padding: 20px; }}
</style></head><body>
<div class="header">
    <h2>Lead Management</h2>
    <div class="stats">
        <div class="stat"><div class="val">{sum(1 for l in leads if l.get('temperature')=='hot')}</div><div class="lbl">Hot Leads</div></div>
        <div class="stat"><div class="val">{sum(1 for l in leads if l.get('status') in ('qualified','appointment_booked'))}</div><div class="lbl">Qualified</div></div>
        <div class="stat"><div class="val">{len(leads)}</div><div class="lbl">Total</div></div>
    </div>
</div>
<div class="kanban">{columns_html}</div>
</body></html>"""
    screenshot_html(html, os.path.join(SCREENSHOT_DIR, "02_lead_management.png"))


# ── GIG IMAGE 3: CALL ANALYTICS ──────────────────────────────────────
def create_call_analytics(dashboard, calls):
    ov = dashboard["overview"]
    chart = dashboard["charts"]
    
    outcomes_html = ""
    max_count = max((o["count"] for o in chart.get("call_outcomes", [])), default=1)
    colors = ["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
    for i, o in enumerate(chart.get("call_outcomes", [])[:6]):
        pct = (o["count"] / max_count) * 100
        outcomes_html += f"""<div class="outcome-row">
            <span class="outcome-label">{o['outcome'].replace('_',' ').title()}</span>
            <div class="outcome-bar-bg"><div class="outcome-bar" style="width:{pct}%; background:{colors[i%len(colors)]}"></div></div>
            <span class="outcome-val">{o['count']}</span>
        </div>"""
    
    recent_calls_html = ""
    for c in calls[:5]:
        direction_color = "#3b82f6" if c.get("direction") == "inbound" else "#8b5cf6"
        direction_icon = "↗" if c.get("direction") == "inbound" else "↙"
        outcome = (c.get("outcome") or "unknown").replace("_", " ").title()
        recent_calls_html += f"""<div class="call-row">
            <div class="call-dir" style="color:{direction_color}">{direction_icon}</div>
            <div class="call-info">
                <div class="call-name">Call #{c.get('id', '?')}</div>
                <div class="call-meta">{c.get('duration_seconds', 0)//60}:{c.get('duration_seconds', 0)%60:02d}</div>
            </div>
            <div class="call-score" style="color: {'#22c55e' if c.get('qualification_score',0) >= 70 else '#f59e0b' if c.get('qualification_score',0) >= 40 else '#64748b'}">{c.get('qualification_score', 0)}</div>
            <div class="call-outcome">{outcome}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: 1280px; height: 720px;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 40%, #0d1117 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    padding: 40px; color: white; overflow: hidden;
}}
.header h2 {{
    font-size: 28px; font-weight: 700; margin-bottom: 24px;
    background: linear-gradient(135deg, #fff, #c7d2fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.panel {{
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 24px;
}}
.panel h3 {{ font-size: 16px; font-weight: 600; color: #e2e8f0; margin-bottom: 4px; }}
.panel .sub {{ font-size: 12px; color: #64748b; margin-bottom: 16px; }}
.stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
.stat-box {{
    background: rgba(255,255,255,0.04); border-radius: 10px;
    padding: 16px; text-align: center;
}}
.stat-box .num {{ font-size: 28px; font-weight: 700; }}
.stat-box .lbl {{ font-size: 11px; color: #64748b; margin-top: 4px; }}
.outcome-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
.outcome-label {{ width: 120px; font-size: 12px; color: #94a3b8; text-align: right; }}
.outcome-bar-bg {{
    flex: 1; height: 24px; background: rgba(255,255,255,0.04);
    border-radius: 6px; overflow: hidden;
}}
.outcome-bar {{ height: 100%; border-radius: 6px; transition: width 0.5s; }}
.outcome-val {{ width: 30px; font-size: 13px; font-weight: 600; color: #e2e8f0; }}
.call-row {{
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px; background: rgba(255,255,255,0.03);
    border-radius: 8px; margin-bottom: 6px;
}}
.call-dir {{ font-size: 18px; font-weight: 700; }}
.call-name {{ font-size: 13px; font-weight: 600; color: #e2e8f0; }}
.call-meta {{ font-size: 11px; color: #64748b; }}
.call-info {{ flex: 1; }}
.call-score {{ font-size: 15px; font-weight: 700; width: 40px; text-align: center; }}
.call-outcome {{ font-size: 11px; color: #94a3b8; width: 100px; text-align: right; }}
</style></head><body>
<div class="header"><h2>Call Analytics & Insights</h2></div>
<div class="stat-grid" style="margin-bottom:24px;">
    <div class="stat-box"><div class="num" style="color:#8b5cf6">{ov['total_calls']}</div><div class="lbl">Total Calls</div></div>
    <div class="stat-box"><div class="num" style="color:#3b82f6">{ov['answered_calls']}</div><div class="lbl">Answered</div></div>
    <div class="stat-box"><div class="num" style="color:#10b981">{ov['qualified_leads']}</div><div class="lbl">Qualified</div></div>
    <div class="stat-box"><div class="num" style="color:#f59e0b">{ov['appointments_booked']}</div><div class="lbl">Booked</div></div>
</div>
<div class="grid">
    <div class="panel">
        <h3>Call Outcomes</h3>
        <div class="sub">Distribution of call results</div>
        {outcomes_html}
    </div>
    <div class="panel">
        <h3>Recent Calls</h3>
        <div class="sub">Latest voice interactions</div>
        {recent_calls_html}
    </div>
</div>
</body></html>"""
    screenshot_html(html, os.path.join(SCREENSHOT_DIR, "03_call_analytics.png"))


# ── GIG IMAGE 4: APPOINTMENT CALENDAR ────────────────────────────────
def create_appointments(appointments):
    # Build a month calendar view
    import calendar
    import datetime
    
    today = datetime.date.today()
    year, month = today.year, today.month
    cal = calendar.monthcalendar(year, month)
    month_name = today.strftime("%B %Y")
    
    # Map appointments to days
    appt_map = {}
    for a in appointments:
        try:
            dt = datetime.datetime.fromisoformat(a.get("start_time", "").replace("Z", "+00:00"))
            if dt.month == month and dt.year == year:
                day = dt.day
                if day not in appt_map:
                    appt_map[day] = []
                appt_map[day].append(a)
        except:
            pass
    
    status_colors = {
        "scheduled": ("#3b82f6", "rgba(59,130,246,0.15)"),
        "confirmed": ("#10b981", "rgba(16,185,129,0.15)"),
        "completed": ("#6366f1", "rgba(99,102,241,0.15)"),
        "cancelled": ("#ef4444", "rgba(239,68,68,0.15)"),
    }
    
    days_html = ""
    for week in cal:
        for day in week:
            if day == 0:
                days_html += '<div class="cal-day other"></div>'
                continue
            
            is_today = day == today.day
            today_class = " today" if is_today else ""
            
            events_html = ""
            for a in appt_map.get(day, [])[:2]:
                status = a.get("status", "scheduled")
                color, bg = status_colors.get(status, ("#64748b", "rgba(100,116,139,0.15)"))
                name = a.get("customer_name", "Client")
                events_html += f'<div class="cal-event" style="background:{bg}; color:{color}; border-left: 2px solid {color}">{name}</div>'
            
            more = ""
            count = len(appt_map.get(day, []))
            if count > 2:
                more = f'<div class="cal-more">+{count-2} more</div>'
            
            days_html += f"""<div class="cal-day{today_class}">
                <span class="day-num">{day}</span>
                <div class="day-events">{events_html}{more}</div>
            </div>"""
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: 1280px; height: 720px;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 40%, #0d1117 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    padding: 40px; color: white; overflow: hidden;
}}
.header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px;
}}
.header h2 {{
    font-size: 28px; font-weight: 700;
    background: linear-gradient(135deg, #fff, #c7d2fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.header .month {{ font-size: 16px; color: #94a3b8; }}
.cal-grid {{
    display: grid; grid-template-columns: repeat(7, 1fr);
    gap: 4px; background: rgba(255,255,255,0.02);
    border-radius: 14px; border: 1px solid rgba(255,255,255,0.06);
    overflow: hidden;
}}
.cal-header {{
    padding: 12px; text-align: center; font-size: 12px;
    font-weight: 600; color: #64748b; text-transform: uppercase;
    background: rgba(255,255,255,0.03);
}}
.cal-day {{
    min-height: 85px; padding: 8px;
    border: 1px solid rgba(255,255,255,0.04);
}}
.cal-day.other {{ opacity: 0.3; }}
.cal-day.today {{
    background: rgba(99,102,241,0.08);
    border-color: rgba(99,102,241,0.2);
}}
.day-num {{
    font-size: 13px; font-weight: 600; color: #94a3b8;
    display: block; margin-bottom: 4px;
}}
.cal-day.today .day-num {{ color: #818cf8; font-weight: 700; }}
.day-events {{ display: flex; flex-direction: column; gap: 2px; }}
.cal-event {{
    font-size: 10px; padding: 2px 6px; border-radius: 4px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.cal-more {{ font-size: 9px; color: #64748b; text-align: center; }}
</style></head><body>
<div class="header">
    <h2>Appointment Calendar</h2>
    <span class="month">{month_name}</span>
</div>
<div class="cal-grid">
    <div class="cal-header">Sun</div><div class="cal-header">Mon</div>
    <div class="cal-header">Tue</div><div class="cal-header">Wed</div>
    <div class="cal-header">Thu</div><div class="cal-header">Fri</div>
    <div class="cal-header">Sat</div>
    {days_html}
</div>
</body></html>"""
    screenshot_html(html, os.path.join(SCREENSHOT_DIR, "04_appointments.png"))


# ── GIG IMAGE 5: HOW IT WORKS ───────────────────────────────────────
def create_how_it_works():
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    width: 1280px; height: 720px;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 40%, #0d1117 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    padding: 48px 60px; color: white; overflow: hidden;
    display: flex; flex-direction: column;
}
h2 {
    font-size: 32px; font-weight: 700; text-align: center; margin-bottom: 8px;
    background: linear-gradient(135deg, #fff, #c7d2fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.subtitle { text-align: center; color: #94a3b8; font-size: 15px; margin-bottom: 48px; }
.steps { display: flex; gap: 32px; flex: 1; align-items: stretch; }
.step {
    flex: 1; background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 32px 24px;
    display: flex; flex-direction: column; align-items: center;
    text-align: center; position: relative;
}
.step-num {
    width: 48px; height: 48px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 700; margin-bottom: 20px;
}
.step:nth-child(1) .step-num { background: rgba(99,102,241,0.2); color: #818cf8; }
.step:nth-child(2) .step-num { background: rgba(59,130,246,0.2); color: #60a5fa; }
.step:nth-child(3) .step-num { background: rgba(16,185,129,0.2); color: #34d399; }
.step:nth-child(4) .step-num { background: rgba(245,158,11,0.2); color: #fbbf24; }
.step-icon { font-size: 48px; margin-bottom: 16px; }
.step h3 { font-size: 18px; font-weight: 600; color: #e2e8f0; margin-bottom: 8px; }
.step p { font-size: 13px; color: #94a3b8; line-height: 1.5; }
.arrow {
    position: absolute; right: -22px; top: 50%;
    transform: translateY(-50%);
    font-size: 20px; color: #475569;
}
.step:last-child .arrow {{ display: none; }}
.footer {{
    text-align: center; margin-top: 36px;
    padding: 16px; background: rgba(255,255,255,0.03);
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
}}
.footer p {{ font-size: 14px; color: #94a3b8; }}
.footer strong {{ color: #e2e8f0; }}
</style></head><body>
<h2>How It Works</h2>
<p class="subtitle">From order to live AI receptionist in 3 simple steps</p>
<div class="steps">
    <div class="step">
        <div class="step-num">1</div>
        <div class="step-icon">📋</div>
        <h3>Tell Me About Your Business</h3>
        <p>Share your business type, phone number, hours, and what your AI should say. I'll handle the rest.</p>
        <span class="arrow">→</span>
    </div>
    <div class="step">
        <div class="step-num">2</div>
        <div class="step-icon">⚡</div>
        <h3>I Build Your System</h3>
        <p>AI agent + dashboard + integrations — the complete system, not just a config. 2-3 days.</p>
        <span class="arrow">→</span>
    </div>
    <div class="step">
        <div class="step-num">3</div>
        <div class="step-icon">🧪</div>
        <h3>Test & Fine-Tune</h3>
        <p>Test with real calls. I adjust the script based on real conversations until it sounds perfect.</p>
        <span class="arrow">→</span>
    </div>
    <div class="step">
        <div class="step-num">4</div>
        <div class="step-icon">🚀</div>
        <h3>Go Live 24/7</h3>
        <p>Your AI receptionist answers calls, qualifies leads, and books appointments — all day, every day.</p>
    </div>
</div>
<div class="footer">
    <p>✨ <strong>No coding required</strong> — I handle all technical setup. You just use the dashboard.</p>
</div>
</body></html>"""
    screenshot_html(html, os.path.join(SCREENSHOT_DIR, "05_how_it_works.png"))


# ── GIG IMAGE 6: FEATURES OVERVIEW ───────────────────────────────────
def create_features_overview():
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    width: 1280px; height: 720px;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 40%, #0d1117 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    padding: 48px 60px; color: white; overflow: hidden;
}
h2 {
    font-size: 32px; font-weight: 700; text-align: center; margin-bottom: 40px;
    background: linear-gradient(135deg, #fff, #c7d2fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
}
.card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 28px 24px;
    transition: all 0.2s;
}
.card:hover { background: rgba(255,255,255,0.05); }
.card-icon {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin-bottom: 16px;
}
.card h3 { font-size: 16px; font-weight: 600; color: #e2e8f0; margin-bottom: 6px; }
.card p { font-size: 13px; color: #94a3b8; line-height: 1.5; }
.icon-1 { background: rgba(99,102,241,0.15); }
.icon-2 { background: rgba(59,130,246,0.15); }
.icon-3 { background: rgba(16,185,129,0.15); }
.icon-4 { background: rgba(245,158,11,0.15); }
.icon-5 { background: rgba(239,68,68,0.15); }
.icon-6 { background: rgba(139,92,246,0.15); }
</style></head><body>
<h2>What You Get</h2>
<div class="grid">
    <div class="card">
        <div class="card-icon icon-1">📞</div>
        <h3>AI Voice Agent</h3>
        <p>Natural-sounding AI that answers calls, collects info, and qualifies leads 24/7.</p>
    </div>
    <div class="card">
        <div class="card-icon icon-2">📊</div>
        <h3>Analytics Dashboard</h3>
        <p>10+ page dashboard with KPIs, charts, call analytics, and real-time metrics.</p>
    </div>
    <div class="card">
        <div class="card-icon icon-3">👥</div>
        <h3>Lead Management</h3>
        <p>Kanban board with lead scoring (0-100), temperature tracking, and pipeline view.</p>
    </div>
    <div class="card">
        <div class="card-icon icon-4">📅</div>
        <h3>Appointment Booking</h3>
        <p>AI books appointments directly into your calendar. Google Calendar sync included.</p>
    </div>
    <div class="card">
        <div class="card-icon icon-5">📋</div>
        <h3>Call Summaries</h3>
        <p>AI-generated call summaries with intent, score, transcript, and next actions.</p>
    </div>
    <div class="card">
        <div class="card-icon icon-6">🔄</div>
        <h3>Campaign Management</h3>
        <p>Outbound calling campaigns with metrics, lead lists, and performance tracking.</p>
    </div>
</div>
</body></html>"""
    screenshot_html(html, os.path.join(SCREENSHOT_DIR, "06_features.png"))


def main():
    print("🔑 Getting auth token...")
    token = get_token()
    
    print("📊 Fetching dashboard data...")
    dashboard = get_dashboard(token)
    
    print("👥 Fetching leads...")
    leads = get_leads(token)
    print(f"   Found {len(leads)} leads")
    
    print("📞 Fetching calls...")
    calls = get_calls(token)
    print(f"   Found {len(calls)} calls")
    
    print("📅 Fetching appointments...")
    appointments = get_appointments(token)
    print(f"   Found {len(appointments)} appointments")
    
    print("\n🖼️  Generating gig images...\n")
    
    create_main_thumbnail(dashboard)
    create_lead_management(leads)
    create_call_analytics(dashboard, calls)
    create_appointments(appointments)
    create_how_it_works()
    create_features_overview()
    
    print(f"\n✅ All images saved to: {SCREENSHOT_DIR}")
    print("\nFiles generated:")
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        if f.endswith(".png"):
            size = os.path.getsize(os.path.join(SCREENSHOT_DIR, f))
            print(f"  📸 {f} ({size:,} bytes)")


if __name__ == "__main__":
    main()
