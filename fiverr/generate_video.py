#!/usr/bin/env python3
"""
VoiceFlow AI — Fiverr Gig Demo Video Generator
Creates a professional 60-75 second demo video with:
- Animated text frames (slide-based)
- Voice narration (gTTS)
- Smooth transitions
- Professional styling
Output: fiverr/voiceflow-demo.mp4
"""

import os
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    concatenate_audioclips,
    TextClip,
    vfx,
)

# ─── Config ───────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1920, 1080
FPS = 30
BASE_DIR = Path(__file__).parent
FRAMES_DIR = BASE_DIR / "frames"
AUDIO_DIR = BASE_DIR / "audio"
OUTPUT_FILE = BASE_DIR / "voiceflow-demo.mp4"

# Colors (matching the app's dark theme)
BG_DARK = (15, 17, 23)          # #0f1117
BG_CARD = (25, 28, 40)          # #191c28
ACCENT_PURPLE = (99, 102, 241)  # #6366f1
ACCENT_BLUE = (59, 130, 246)    # #3b82f6
ACCENT_GREEN = (16, 185, 129)   # #10b981
ACCENT_AMBER = (245, 158, 11)   # #f59e0b
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (156, 163, 175)
TEXT_DIM = (107, 114, 128)


def get_font(size, bold=False):
    """Get font with fallback."""
    font_paths = [
        "C:/Windows/Fonts/segoeui.ttf" if not bold else "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_gradient_bar(draw, x, y, w, h, color, value_pct):
    """Draw a gradient progress bar."""
    # Background
    draw.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=(40, 44, 60))
    # Fill
    fill_w = int(w * value_pct)
    if fill_w > 0:
        draw.rounded_rectangle((x, y, x + fill_w, y + h), radius=h // 2, fill=color)


def draw_icon_circle(draw, cx, cy, r, color):
    """Draw a simple circle icon placeholder."""
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)


# ─── Scene Generators ─────────────────────────────────────────────────────────

def scene_hook():
    """Scene 1: Hook — 'What if your phone was answered 24/7 by an AI?'"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Decorative gradient circles
    for i, (cx, cy, r, alpha) in enumerate([
        (300, 300, 200, 30), (1600, 700, 250, 25), (960, 200, 150, 20)
    ]):
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*ACCENT_PURPLE, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Phone icon
    draw.rounded_rectangle((860, 250, 1060, 500), radius=30, fill=ACCENT_PURPLE)
    draw.rounded_rectangle((880, 280, 1040, 460), radius=15, fill=BG_DARK)
    # Phone screen content - wave lines
    for yy in range(310, 440, 20):
        draw.line((900, yy, 1020, yy), fill=ACCENT_GREEN, width=2)
    # Phone dot
    draw.ellipse((940, 465, 980, 490), fill=ACCENT_PURPLE)

    # Main text
    font_big = get_font(64, bold=True)
    font_sub = get_font(32)

    # "What if your phone" — line 1
    text1 = "What if your phone was answered"
    bbox = draw.textbbox((0, 0), text1, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 550), text1, fill=TEXT_WHITE, font=font_big)

    # "24/7 by an AI?" — line 2 (accent color)
    text2 = "24/7 by an AI?"
    bbox2 = draw.textbbox((0, 0), text2, font=font_big)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((WIDTH - tw2) // 2, 640), text2, fill=ACCENT_PURPLE, font=font_big)

    # Subtitle
    text3 = "Meet VoiceFlow AI — Your AI Voice Receptionist"
    bbox3 = draw.textbbox((0, 0), text3, font=font_sub)
    tw3 = bbox3[2] - bbox3[0]
    draw.text(((WIDTH - tw3) // 2, 760), text3, fill=TEXT_GRAY, font=font_sub)

    return img


def scene_problem():
    """Scene 2: Problem — Businesses miss calls."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    font_big = get_font(58, bold=True)
    font_stat = get_font(120, bold=True)
    font_sub = get_font(28)
    font_small = get_font(22)

    # Problem statement
    t1 = "The Problem"
    bbox = draw.textbbox((0, 0), t1, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 80), t1, fill=ACCENT_AMBER, font=font_big)

    # Big stat: 60%
    t2 = "60%"
    bbox2 = draw.textbbox((0, 0), t2, font=font_stat)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((WIDTH - tw2) // 2, 180), t2, fill=TEXT_WHITE, font=font_stat)

    t3 = "of inbound calls go unanswered"
    bbox3 = draw.textbbox((0, 0), t3, font=font_sub)
    tw3 = bbox3[2] - bbox3[0]
    draw.text(((WIDTH - tw3) // 2, 320), t3, fill=TEXT_GRAY, font=font_sub)

    # Three pain points as cards
    problems = [
        ("Missed Revenue", "Every missed call is a lost customer.", ACCENT_AMBER),
        ("No Follow-up", "Leads go cold without timely response.", ACCENT_BLUE),
        ("Overwhelmed Staff", "Receptionists can't handle peak hours.", ACCENT_GREEN),
    ]

    card_w = 500
    card_h = 220
    gap = 40
    start_x = (WIDTH - (3 * card_w + 2 * gap)) // 2

    for i, (title, desc, color) in enumerate(problems):
        x = start_x + i * (card_w + gap)
        y = 430
        draw_rounded_rect(draw, (x, y, x + card_w, y + card_h), radius=16, fill=BG_CARD)
        # Color accent bar at top
        draw.rounded_rectangle((x, y, x + card_w, y + 6), radius=3, fill=color)
        # Title
        draw.text((x + 30, y + 30), title, fill=color, font=get_font(28, bold=True))
        # Description
        draw.text((x + 30, y + 80), desc, fill=TEXT_GRAY, font=get_font(22))

    # Bottom stat
    t4 = "The average business loses $1,200/month from missed calls"
    bbox4 = draw.textbbox((0, 0), t4, font=font_small)
    tw4 = bbox4[2] - bbox4[0]
    draw.text(((WIDTH - tw4) // 2, 730), t4, fill=ACCENT_AMBER, font=font_small)

    return img


def scene_solution():
    """Scene 3: Solution — VoiceFlow AI overview."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    font_big = get_font(54, bold=True)
    font_sub = get_font(26)
    font_label = get_font(20)

    # Header
    t1 = "The Solution: VoiceFlow AI"
    bbox = draw.textbbox((0, 0), t1, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 60), t1, fill=ACCENT_GREEN, font=font_big)

    t2 = "AI-powered voice agent that answers calls, qualifies leads, and books appointments"
    bbox2 = draw.textbbox((0, 0), t2, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((WIDTH - tw2) // 2, 135), t2, fill=TEXT_GRAY, font=font_sub)

    # Architecture diagram — simplified
    # AI Agent box
    draw_rounded_rect(draw, (760, 210, 1160, 310), radius=12, fill=ACCENT_PURPLE)
    t_ai = "AI Voice Agent"
    bb = draw.textbbox((0, 0), t_ai, font=get_font(26, bold=True))
    draw.text(((WIDTH - (bb[2] - bb[0])) // 2, 245), t_ai, fill=TEXT_WHITE, font=get_font(26, bold=True))

    # Arrows down
    for x_off in [300, 600, 900]:
        draw.line((WIDTH // 2, 310, x_off + 160, 370), fill=TEXT_DIM, width=2)

    # Feature boxes
    features = [
        ("📞", "Receptionist", "Answers inbound calls", ACCENT_BLUE),
        ("📊", "Lead Scoring", "Qualifies leads 0-100", ACCENT_GREEN),
        ("📅", "Appointments", "Books & manages calendar", ACCENT_AMBER),
    ]

    box_w = 320
    box_h = 160
    start_x = (WIDTH - (3 * box_w + 2 * 60)) // 2

    for i, (emoji, title, desc, color) in enumerate(features):
        x = start_x + i * (box_w + 60)
        y = 380
        draw_rounded_rect(draw, (x, y, x + box_w, y + box_h), radius=12, fill=BG_CARD)
        draw.rounded_rectangle((x, y, x + box_w, y + 5), radius=3, fill=color)
        draw.text((x + 20, y + 25), title, fill=color, font=get_font(24, bold=True))
        draw.text((x + 20, y + 70), desc, fill=TEXT_GRAY, font=get_font(18))

    # Bottom flow
    t3 = "Inbound Call → AI Answers → Qualifies Lead → Books Appointment → Follow-up Sent"
    bb3 = draw.textbbox((0, 0), t3, font=get_font(22))
    draw.text(((WIDTH - (bb3[2] - bb3[0])) // 2, 600), t3, fill=ACCENT_PURPLE, font=get_font(22))

    # Works with
    t4 = "Works with: Retell AI  •  Vapi AI  •  Google Calendar  •  Any CRM"
    bb4 = draw.textbbox((0, 0), t4, font=get_font(20))
    draw.text(((WIDTH - (bb4[2] - bb4[0])) // 2, 660), t4, fill=TEXT_DIM, font=get_font(20))

    return img


def scene_dashboard():
    """Scene 4: Dashboard overview with mock KPIs."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    font_title = get_font(42, bold=True)
    font_kpi_val = get_font(48, bold=True)
    font_kpi_label = get_font(18)
    font_section = get_font(24, bold=True)
    font_small = get_font(16)

    # Header
    draw.text((60, 40), "VoiceFlow AI — Dashboard", fill=TEXT_WHITE, font=font_title)

    # Sidebar
    draw_rounded_rect(draw, (0, 0, 220, HEIGHT), radius=0, fill=(20, 22, 32))
    sidebar_items = [
        ("Dashboard", True), ("Calls", False), ("Leads", False),
        ("Appointments", False), ("Campaigns", False), ("Settings", False),
    ]
    for i, (label, active) in enumerate(sidebar_items):
        y = 100 + i * 50
        if active:
            draw.rounded_rectangle((10, y - 5, 210, y + 35), radius=8, fill=ACCENT_PURPLE)
            draw.text((40, y), label, fill=TEXT_WHITE, font=get_font(18, bold=True))
        else:
            draw.text((40, y), label, fill=TEXT_DIM, font=get_font(18))

    # KPI Cards
    kpis = [
        ("Total Calls", "247", "+12%", ACCENT_PURPLE),
        ("Leads", "89", "+8%", ACCENT_BLUE),
        ("Appointments", "34", "+15%", ACCENT_GREEN),
        ("Conversion", "72%", "+5%", ACCENT_AMBER),
    ]

    card_w = 340
    card_h = 120
    start_x = 280

    for i, (label, value, trend, color) in enumerate(kpis):
        x = start_x + i * (card_w + 30)
        y = 120
        draw_rounded_rect(draw, (x, y, x + card_w, y + card_h), radius=12, fill=BG_CARD)
        # Icon circle
        draw_icon_circle(draw, x + 35, y + 35, 20, color)
        # Value
        draw.text((x + 70, y + 20), value, fill=TEXT_WHITE, font=font_kpi_val)
        # Label
        draw.text((x + 70, y + 75), label, fill=TEXT_GRAY, font=font_kpi_label)
        # Trend
        draw.text((x + card_w - 70, y + 20), trend, fill=ACCENT_GREEN, font=get_font(16, bold=True))

    # Chart area — mock line chart
    chart_x, chart_y = 280, 280
    chart_w, chart_h = 780, 320
    draw_rounded_rect(draw, (chart_x, chart_y, chart_x + chart_w, chart_y + chart_h), radius=12, fill=BG_CARD)
    draw.text((chart_x + 20, chart_y + 15), "Calls Over Time", fill=TEXT_WHITE, font=font_section)

    # Mock chart lines
    points_data = [
        [(0, 180), (130, 120), (260, 150), (390, 80), (520, 110), (650, 60), (780, 40)],
        [(0, 160), (130, 140), (260, 100), (390, 130), (520, 90), (650, 100), (780, 70)],
    ]
    colors_chart = [ACCENT_PURPLE, ACCENT_BLUE]

    for pts, color in zip(points_data, colors_chart):
        shifted = [(chart_x + 30 + px, chart_y + 50 + py) for px, py in pts]
        draw.line(shifted, fill=color, width=3)
        for sx, sy in shifted:
            draw.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=color)

    # Right panel — Recent Calls
    rp_x, rp_y = 1100, 280
    rp_w, rp_h = 760, 320
    draw_rounded_rect(draw, (rp_x, rp_y, rp_x + rp_w, rp_y + rp_h), radius=12, fill=BG_CARD)
    draw.text((rp_x + 20, rp_y + 15), "Recent Calls", fill=TEXT_WHITE, font=font_section)

    calls_mock = [
        ("Sarah Johnson", "Inbound", "2:34", "Qualified", ACCENT_GREEN),
        ("Mike Chen", "Outbound", "5:12", "Booked", ACCENT_BLUE),
        ("Emily Davis", "Inbound", "1:45", "Follow-up", ACCENT_AMBER),
        ("James Wilson", "Outbound", "3:20", "Qualified", ACCENT_GREEN),
        ("Lisa Brown", "Inbound", "0:45", "Missed", ACCENT_AMBER),
    ]

    for i, (name, direction, dur, status, color) in enumerate(calls_mock):
        row_y = rp_y + 55 + i * 50
        draw.text((rp_x + 20, row_y), name, fill=TEXT_WHITE, font=get_font(17))
        draw.text((rp_x + 250, row_y), direction, fill=TEXT_GRAY, font=get_font(16))
        draw.text((rp_x + 400, row_y), dur, fill=TEXT_GRAY, font=get_font(16))
        # Status dot
        draw.ellipse((rp_x + 550, row_y + 3, rp_x + 563, row_y + 16), fill=color)
        draw.text((rp_x + 570, row_y), status, fill=color, font=get_font(16))

    # Bottom — Activity Feed
    af_y = 640
    draw_rounded_rect(draw, (280, af_y, 1860, af_y + 180), radius=12, fill=BG_CARD)
    draw.text((300, af_y + 15), "Activity Feed", fill=TEXT_WHITE, font=font_section)

    activities = [
        ("New lead: Sarah Johnson — Inbound call, qualified (Score: 85)", ACCENT_GREEN),
        ("Appointment booked: Mike Chen — Roof inspection, Aug 26 at 10 AM", ACCENT_BLUE),
        ("Follow-up scheduled: Emily Davis — Callback in 3 days", ACCENT_AMBER),
        ("Campaign started: Summer Roofing Outreach — 25 leads", ACCENT_PURPLE),
    ]

    for i, (text, color) in enumerate(activities):
        ay = af_y + 50 + i * 30
        draw.ellipse((310, ay + 5, 322, ay + 17), fill=color)
        draw.text((335, ay), text, fill=TEXT_GRAY, font=get_font(16))

    return img


def scene_features():
    """Scene 5: Feature highlights."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    font_big = get_font(48, bold=True)
    font_feat = get_font(24, bold=True)
    font_desc = get_font(18)

    t1 = "Everything You Need"
    bbox = draw.textbbox((0, 0), t1, font=font_big)
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 50), t1, fill=TEXT_WHITE, font=font_big)

    features = [
        ("AI Voice Receptionist", "Answers calls 24/7, sounds human", ACCENT_PURPLE, "🎙️"),
        ("Lead Qualification", "Scores leads 0-100 automatically", ACCENT_BLUE, "📊"),
        ("Appointment Booking", "Schedules & confirms via calendar", ACCENT_GREEN, "📅"),
        ("Call Summaries", "AI-generated transcripts & insights", ACCENT_AMBER, "📝"),
        ("CRM Pipeline", "Kanban board with drag-and-drop", ACCENT_PURPLE, "🗂️"),
        ("Campaign Manager", "Outbound calling campaigns", ACCENT_BLUE, "📢"),
        ("Analytics Dashboard", "Real-time KPIs and charts", ACCENT_GREEN, "📈"),
        ("Follow-up System", "Automated scheduling & reminders", ACCENT_AMBER, "🔔"),
    ]

    cols, rows = 4, 2
    card_w, card_h = 380, 160
    gap_x, gap_y = 40, 30
    start_x = (WIDTH - (cols * card_w + (cols - 1) * gap_x)) // 2
    start_y = 140

    for i, (title, desc, color, emoji) in enumerate(features):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)

        draw_rounded_rect(draw, (x, y, x + card_w, y + card_h), radius=12, fill=BG_CARD)
        draw.rounded_rectangle((x, y, x + card_w, y + 5), radius=3, fill=color)

        # Emoji circle
        draw_icon_circle(draw, x + 35, y + 45, 22, color)

        draw.text((x + 70, y + 30), title, fill=TEXT_WHITE, font=font_feat)
        draw.text((x + 30, y + 80), desc, fill=TEXT_GRAY, font=font_desc)

    # Bottom text
    t2 = "React + FastAPI • Fully Documented • 36 Tests • Docker Ready"
    bb2 = draw.textbbox((0, 0), t2, font=get_font(22))
    draw.text(((WIDTH - (bb2[2] - bb2[0])) // 2, 530), t2, fill=TEXT_DIM, font=get_font(22))

    # Tech stack boxes
    techs = [
        ("React 19", ACCENT_BLUE), ("FastAPI", ACCENT_GREEN),
        ("SQLAlchemy", ACCENT_AMBER), ("Tailwind CSS", ACCENT_PURPLE),
        ("Retell AI", ACCENT_BLUE), ("Vapi AI", ACCENT_GREEN),
    ]

    tw_start = (WIDTH - (6 * 170 + 5 * 20)) // 2
    for i, (tech, color) in enumerate(techs):
        tx = tw_start + i * 190
        ty = 590
        draw_rounded_rect(draw, (tx, ty, tx + 170, ty + 50), radius=25, fill=color)
        tbb = draw.textbbox((0, 0), tech, font=get_font(18, bold=True))
        draw.text((tx + (170 - (tbb[2] - tbb[0])) // 2, ty + 14), tech, fill=TEXT_WHITE, font=get_font(18, bold=True))

    # Industries
    t3 = "Perfect for: Real Estate • Dental/Medical • Home Services • Law Firms • Insurance"
    bb3 = draw.textbbox((0, 0), t3, font=get_font(20))
    draw.text(((WIDTH - (bb3[2] - bb3[0])) // 2, 680), t3, fill=TEXT_GRAY, font=get_font(20))

    return img


def scene_cta():
    """Scene 6: Call to Action."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Gradient-ish circles
    for cx, cy, r, alpha in [(400, 400, 300, 20), (1500, 600, 250, 15), (960, 900, 200, 25)]:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*ACCENT_PURPLE, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    font_huge = get_font(72, bold=True)
    font_big = get_font(40, bold=True)
    font_sub = get_font(28)
    font_small = get_font(22)

    # Main CTA
    t1 = "Get Your AI Voice Agent"
    bb1 = draw.textbbox((0, 0), t1, font=font_huge)
    draw.text(((WIDTH - (bb1[2] - bb1[0])) // 2, 250), t1, fill=TEXT_WHITE, font=font_huge)

    t2 = "Built Today"
    bb2 = draw.textbbox((0, 0), t2, font=font_huge)
    draw.text(((WIDTH - (bb2[2] - bb2[0])) // 2, 340), t2, fill=ACCENT_PURPLE, font=font_huge)

    # Button mockup
    btn_w, btn_h = 420, 70
    btn_x = (WIDTH - btn_w) // 2
    btn_y = 470
    draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), radius=35, fill=ACCENT_PURPLE)
    t_btn = "Order Now on Fiverr"
    bb_btn = draw.textbbox((0, 0), t_btn, font=font_big)
    draw.text((btn_x + (btn_w - (bb_btn[2] - bb_btn[0])) // 2, btn_y + 15), t_btn, fill=TEXT_WHITE, font=font_big)

    # Packages
    packages = [
        ("Basic", "$297", "AI Receptionist Setup", ACCENT_BLUE),
        ("Standard", "$497", "Complete AI Sales System", ACCENT_GREEN),
        ("Premium", "$797", "Full Automation Suite", ACCENT_AMBER),
    ]

    pkg_w, pkg_h = 340, 200
    pkg_gap = 40
    pkg_start = (WIDTH - (3 * pkg_w + 2 * pkg_gap)) // 2

    for i, (name, price, desc, color) in enumerate(packages):
        x = pkg_start + i * (pkg_w + pkg_gap)
        y = 590
        draw_rounded_rect(draw, (x, y, x + pkg_w, y + pkg_h), radius=12, fill=BG_CARD)
        draw.rounded_rectangle((x, y, x + pkg_w, y + 5), radius=3, fill=color)
        draw.text((x + 20, y + 20), name, fill=color, font=get_font(22, bold=True))
        draw.text((x + 20, y + 60), price, fill=TEXT_WHITE, font=get_font(40, bold=True))
        draw.text((x + 20, y + 120), desc, fill=TEXT_GRAY, font=get_font(18))

        if name == "Standard":
            # "Most Popular" badge
            badge = "⭐ Most Popular"
            draw_rounded_rect(draw, (x + pkg_w - 150, y - 20, x + pkg_w + 10, y + 10), radius=12, fill=ACCENT_GREEN)
            draw.text((x + pkg_w - 145, y - 15), badge, fill=TEXT_WHITE, font=get_font(14, bold=True))

    # Footer
    t4 = "VoiceFlow AI — Built with React, FastAPI, Tailwind CSS, Retell AI"
    bb4 = draw.textbbox((0, 0), t4, font=get_font(18))
    draw.text(((WIDTH - (bb4[2] - bb4[0])) // 2, 840), t4, fill=TEXT_DIM, font=get_font(18))

    return img


# ─── Voice Scripts ────────────────────────────────────────────────────────────

VOICE_SCRIPTS = [
    # scene_hook
    "What if your phone was answered 24/7 by an AI that sounds human? "
    "Meet VoiceFlow AI.",

    # scene_problem
    "Businesses miss 60 percent of calls. Every missed call is a lost customer. "
    "You're losing over 1200 dollars a month.",

    # scene_solution
    "VoiceFlow AI answers your calls, qualifies leads, and books appointments. "
    "Works with Retell AI, Vapi AI, and Google Calendar.",

    # scene_dashboard
    "Professional dashboard with real-time analytics. Call transcripts, AI summaries, "
    "lead pipeline, and appointment calendar.",

    # scene_features
    "AI receptionist, lead scoring, appointment booking, CRM, campaigns, analytics, "
    "and follow-ups. React, FastAPI, fully tested.",

    # scene_cta
    "Get your AI voice agent today. From 297 to 797 dollars. Order on Fiverr now.",
]


# ─── Video Builder ────────────────────────────────────────────────────────────

def build_video():
    """Build the complete demo video."""
    print("🎬 VoiceFlow AI — Fiverr Gig Demo Video Generator")
    print("=" * 55)

    scene_funcs = [scene_hook, scene_problem, scene_solution, scene_dashboard, scene_features, scene_cta]
    scene_names = ["Hook", "Problem", "Solution", "Dashboard", "Features", "CTA"]

    # Step 1: Generate frames
    print("\n📸 Generating frames...")
    frame_paths = []
    for i, (func, name) in enumerate(zip(scene_funcs, scene_names)):
        print(f"   [{i+1}/6] {name}...")
        img = func()
        path = FRAMES_DIR / f"scene_{i:02d}_{name.lower()}.png"
        img.save(str(path), "PNG", quality=95)
        frame_paths.append(path)
        print(f"        → Saved: {path.name}")

    # Step 2: Generate voice
    print("\n🎙️ Generating voice narration...")
    audio_paths = []
    for i, (script, name) in enumerate(zip(VOICE_SCRIPTS, scene_names)):
        print(f"   [{i+1}/6] {name}...")
        tts = gTTS(text=script, lang="en", slow=False)
        path = AUDIO_DIR / f"voice_{i:02d}_{name.lower()}.mp3"
        tts.save(str(path))
        audio_paths.append(path)
        print(f"        → Saved: {path.name}")

    # Step 3: Compose video
    print("\n🎬 Composing video clips...")

    clips = []
    audio_clips = []

    for i, (frame_path, audio_path, name) in enumerate(zip(frame_paths, audio_paths, scene_names)):
        print(f"   [{i+1}/6] {name}...")

        # Load audio first to get duration
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration + 1.0  # Add 1s padding after speech

        # Create image clip with fade effects
        clip = (
            ImageClip(str(frame_path))
            .with_duration(duration)
            .with_effects([
                vfx.CrossFadeIn(0.5),
                vfx.CrossFadeOut(0.5),
            ])
        )

        audio_clips.append(audio)
        clips.append(clip)

    # Step 4: Concatenate
    print("\n🔗 Concatenating clips...")
    final_video = concatenate_videoclips(clips, method="compose")

    # Add background silence/audio track
    from moviepy import CompositeAudioClip
    final_audio_clips = []
    current_t = 0
    for audio in audio_clips:
        a = audio.with_start(current_t)
        final_audio_clips.append(a)
        current_t += audio.duration + 1.0

    final_audio = CompositeAudioClip(final_audio_clips)
    final_video = final_video.with_audio(final_audio)

    # Step 5: Export
    print(f"\n💾 Exporting video to: {OUTPUT_FILE}")
    print("   (This may take a few minutes...)")
    final_video.write_videofile(
        str(OUTPUT_FILE),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger="bar",
    )

    # Cleanup
    final_video.close()
    for audio in audio_clips:
        audio.close()

    print(f"\n✅ Demo video created successfully!")
    print(f"   📁 Location: {OUTPUT_FILE}")
    print(f"   📏 Resolution: {WIDTH}x{HEIGHT}")
    print(f"   ⏱️  Duration: ~{int(current_t)}s")
    print(f"   🎞️  FPS: {FPS}")

    return OUTPUT_FILE


if __name__ == "__main__":
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    build_video()
