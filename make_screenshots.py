#!/usr/bin/env python3
"""Render README screenshots of the atlas (docs/index.html) with headless Chrome.

Writes docs/screenshots/{explore,rank,compare,country,banking,mobile}.png.
macOS: uses Google Chrome from /Applications and `sips` to crop the phone shot
(Chrome's headless window cannot be narrower than 500px, so the phone view is
rendered in a 390px iframe and cropped).
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).parent
PAGE = BASE / "docs" / "index.html"
OUT = BASE / "docs" / "screenshots"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# runs before the page script: clean state, fixed theme
PRE = '<script>try{localStorage.clear();localStorage.setItem("oci-state",JSON.stringify({theme:"%s"}))}catch(e){}</script>'


def shot(name, theme, route, size, crop=None):
    with tempfile.TemporaryDirectory() as tmp:
        html = PAGE.read_text(encoding="utf-8").replace("<head>", "<head>\n" + PRE % theme, 1)
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        target, url_hash = page, route
        if crop:  # phone: 390px iframe
            target = Path(tmp) / "phone.html"
            target.write_text(f'<!doctype html><body style="margin:0"><iframe src="page.html{route}" '
                              f'style="width:{crop[0]}px;height:{crop[1]}px;border:0;display:block;margin:0 auto"></iframe></body>')
            url_hash = ""
        png = Path(tmp) / "out.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
                        "--virtual-time-budget=10000", f"--screenshot={png}", target.as_uri() + url_hash],
                       check=True, capture_output=True, timeout=120)
        if crop:
            # sips crops around the centre, where the iframe sits
            subprocess.run(["sips", "--cropToHeightWidth", str(crop[1]), str(crop[0]), str(png)],
                           check=True, capture_output=True)
        OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy(png, OUT / f"{name}.png")
        print("wrote", OUT / f"{name}.png")


if __name__ == "__main__":
    shot("explore", "dark", "#/explore", (1440, 900))
    shot("rank", "dark", "#/rank", (1440, 900))
    shot("compare", "dark", "#/compare/australia,estonia,georgia,united-kingdom,japan", (1440, 1100))
    shot("country", "dark", "#/country/georgia", (1440, 1000))
    shot("banking", "light", "#/banking", (1440, 900))
    shot("mobile", "dark", "#/rank", (600, 1300), crop=(390, 1300))
