"""
bg_server.py — Copies background images into Streamlit's static folder
Run this ONCE before starting the app:  python ui/bg_server.py
"""
import shutil, sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Streamlit serves files from .streamlit/static/
STATIC = ROOT / ".streamlit" / "static"
STATIC.mkdir(parents=True, exist_ok=True)

files = {
    "bg_morning.jpg":   "bg_morning.jpg",
    "bg_afternoon.jpg": "bg_afternoon.jpg",
    "bg_evening.jpg":   "bg_evening.jpg",
    "bg_night.jpg":     "bg_night.jpg",
    "bg_morning.png":   "bg_morning.png",
    "bg_afternoon.png": "bg_afternoon.png",
    "bg_evening.png":   "bg_evening.png",
    "bg_night.png":     "bg_night.png",
}

copied = 0
for src_name, dst_name in files.items():
    src = ASSETS / src_name
    if src.exists():
        shutil.copy2(src, STATIC / dst_name)
        print(f"  Copied: {src_name}")
        copied += 1

if copied == 0:
    print("  No background images found in assets/")
    print(f"  Put your images in: {ASSETS}")
else:
    print(f"\n  {copied} image(s) copied to Streamlit static folder.")
    print("  Now start the app normally.")
