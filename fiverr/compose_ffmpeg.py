#!/usr/bin/env python3
"""Compose video using subprocess + ffmpeg for speed."""
import os, sys, subprocess, json
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"

BASE_DIR = Path(__file__).parent
FRAMES_DIR = BASE_DIR / "frames"
AUDIO_DIR = BASE_DIR / "audio"
OUTPUT_FILE = BASE_DIR / "voiceflow-demo.mp4"
CONCAT_FILE = BASE_DIR / "concat_list.txt"

# Get ffmpeg from imageio
from imageio_ffmpeg import get_ffmpeg_exe
FFMPEG = get_ffmpeg_exe()

scene_names = ["Hook", "Problem", "Solution", "Dashboard", "Features", "CTA"]

def get_duration(audio_path):
    """Get audio duration using mutagen."""
    from mutagen.mp3 import MP3
    try:
        audio = MP3(str(audio_path))
        return audio.info.length
    except:
        return 8.0  # default estimate

print("Getting audio durations...", flush=True)
durations = []
for i, name in enumerate(scene_names):
    audio_path = AUDIO_DIR / f"voice_{i:02d}_{name.lower()}.mp3"
    dur = get_duration(audio_path)
    durations.append(dur + 1.5)  # add padding
    print(f"  {name}: {dur:.1f}s (total: {dur+1.5:.1f}s)", flush=True)

total = sum(durations)
print(f"Total duration: ~{int(total)}s", flush=True)

# Build a concat file for ffmpeg
# We need to create individual video clips per scene, then concat
# Actually, simpler approach: create each scene as a video clip, then concat

print("\nBuilding individual scene clips...", flush=True)

scene_videos = []
for i, name in enumerate(scene_names):
    frame_path = FRAMES_DIR / f"scene_{i:02d}_{name.lower()}.png"
    audio_path = AUDIO_DIR / f"voice_{i:02d}_{name.lower()}.mp3"
    out_path = BASE_DIR / f"scene_{i:02d}.mp4"
    dur = durations[i]
    
    print(f"  [{i+1}/6] {name} ({dur:.1f}s)...", flush=True)
    
    cmd = [
        FFMPEG, "-y",
        "-loop", "1",
        "-i", str(frame_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", f"{dur:.2f}",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-shortest",
        str(out_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-200:]}", flush=True)
        sys.exit(1)
    
    scene_videos.append(out_path)
    print(f"    -> OK", flush=True)

# Now concat all scene videos
print("\nConcatenating all scenes...", flush=True)

with open(CONCAT_FILE, "w") as f:
    for sv in scene_videos:
        f.write(f"file '{sv.as_posix()}'\n")

cmd = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(CONCAT_FILE),
    "-c", "copy",
    str(OUTPUT_FILE)
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
if result.returncode != 0:
    print(f"ERROR during concat: {result.stderr[-300:]}", flush=True)
    sys.exit(1)

# Cleanup temp files
for sv in scene_videos:
    sv.unlink(missing_ok=True)
CONCAT_FILE.unlink(missing_ok=True)

file_size = OUTPUT_FILE.stat().st_size / (1024 * 1024)
print(f"\n=== VIDEO CREATED SUCCESSFULLY ===", flush=True)
print(f"File: {OUTPUT_FILE}", flush=True)
print(f"Size: {file_size:.1f} MB", flush=True)
print(f"Duration: ~{int(total)}s", flush=True)
print(f"Resolution: 1920x1080", flush=True)
