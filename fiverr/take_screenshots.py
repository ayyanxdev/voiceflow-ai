"""Take screenshots of VoiceFlow AI dashboard for Fiverr gig images."""

import subprocess
import time
import os
import json
import urllib.request

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BACKEND = "http://localhost:8000"
FRONTEND = "http://localhost:5173"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

# Create screenshots directory
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def get_token():
    """Login and get JWT token."""
    data = json.dumps({"email": "admin@voiceflow.ai", "password": "admin123"}).encode()
    req = urllib.request.Request(
        f"{BACKEND}/api/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["access_token"]


def take_screenshot(url, output_file, width=1440, height=900, delay=3):
    """Take a screenshot using Chrome headless."""
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={width},{height}",
        f"--screenshot={output_file}",
        "--hide-scrollbars",
        "--virtual-time-budget=5000",
        url,
    ]
    print(f"  Capturing: {output_file}")
    subprocess.run(cmd, capture_output=True, timeout=30)
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"  ✓ Saved ({size:,} bytes)")
    else:
        print(f"  ✗ Failed to capture")


def main():
    token = get_token()
    print(f"Token obtained: {token[:20]}...")

    # We need to set cookies or use the URL with token
    # Chrome headless doesn't easily support auth, so let's use
    # a different approach: create HTML pages that load with the token

    # First, let's try accessing the frontend with cookies
    # The frontend stores the token in localStorage

    pages = [
        ("dashboard", "Dashboard Overview"),
        ("leads", "Lead Management"),
        ("calls", "Call History"),
        ("appointments", "Appointments"),
        ("analytics", "Analytics"),
        ("campaigns", "Campaigns"),
        ("settings", "Settings"),
    ]

    for page_slug, page_name in pages:
        url = f"{FRONTEND}/{page_slug}"
        output = os.path.join(SCREENSHOT_DIR, f"{page_slug}.png")
        print(f"\n[{page_name}]")
        take_screenshot(url, output)

    print(f"\n✅ Screenshots saved to {SCREENSHOT_DIR}")


if __name__ == "__main__":
    main()
