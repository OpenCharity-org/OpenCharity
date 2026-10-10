#!/usr/bin/env python3
"""Render README screenshots of the site (docs/index.html) with headless Chrome.

Writes docs/screenshots/{home,map,rankings,compare,banking,country,dark,mobile}.png.
macOS: uses Google Chrome from /Applications and `sips` to crop the phone shot
(Chrome's headless window cannot be narrower than 500px, so the phone view is
rendered in a 390px iframe and cropped).
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).parent
PAGE = BASE / "docs" / "index.html"
OUT = BASE / "docs" / "screenshots"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# runs before the page script: clean state, fixed theme
PRE = '<script>try{localStorage.clear();localStorage.setItem("oc-site",%s)}catch(e){}</script>'


def shot(name, route, size, theme="light", crop=None):
    with tempfile.TemporaryDirectory() as tmp:
        state = json.dumps(json.dumps({"theme": theme}))
        page = Path(tmp) / "page.html"
        page.write_text(PAGE.read_text(encoding="utf-8").replace("<head>", "<head>\n" + PRE % state, 1), encoding="utf-8")
        target, frag = page.as_uri(), "#" + route
        if crop:  # phone: 390px iframe
            phone = Path(tmp) / "phone.html"
            phone.write_text(f'<!doctype html><body style="margin:0"><iframe src="page.html#{route}" '
                             f'style="width:{crop[0]}px;height:{crop[1]}px;border:0;display:block;margin:0 auto"></iframe></body>')
            target, frag = phone.as_uri(), ""
        png = Path(tmp) / "out.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
                        "--virtual-time-budget=10000", f"--screenshot={png}", target + frag], check=True, capture_output=True, timeout=120)
        if crop:  # sips crops around the centre, where the iframe sits
            subprocess.run(["sips", "--cropToHeightWidth", str(crop[1]), str(crop[0]), str(png)], check=True, capture_output=True)
        OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy(png, OUT / f"{name}.png")
        print("wrote", OUT / f"{name}.png")


if __name__ == "__main__":
    shot("home", "/", (1440, 900))
    shot("map", "/map/estonia", (1440, 900))
    shot("rankings", "/rankings/overall", (1440, 900))
    shot("compare", "/compare/estonia,georgia,united-kingdom", (1440, 900))
    shot("banking", "/banking", (1440, 900))
    shot("country", "/country/georgia", (1440, 800))
    shot("dark", "/map", (1440, 900), theme="dark")
    shot("mobile", "/map/portugal", (600, 844), crop=(390, 844))
