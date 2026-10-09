#!/usr/bin/env python3
"""Render README screenshots of the atlas (docs/index.html) with headless Chrome.

Writes docs/screenshots/{desktop-light,desktop-dark,benchmark,mobile}.png.
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
PRE = '<script>try{localStorage.clear();localStorage.setItem("atlas-theme",JSON.stringify("%s"))}catch(e){}</script>'
# runs after the page script
POST = {
    "plain": "",
    "benchmark": """<script>
const q = s => document.querySelector(s);
["easy", "medium"].forEach(v => q(`.opt[data-f="difficulty"][data-v="${v}"]`).click());
q('.opt[data-f="no_presence"][data-v="yes"]').click();
const r = q("#rankby"); r.value = "custom"; r.dispatchEvent(new Event("change"));
for (const c of ["Estonia", "Georgia", "United Kingdom", "Kyrgyzstan"]) q(`#tbl input[data-cmp="${c}"]`).click();
q(".main").style.display = "none"; q("header.top").style.display = "none";
</script>""",
}


def shot(name, theme, post, size, crop=None):
    with tempfile.TemporaryDirectory() as tmp:
        html = PAGE.read_text(encoding="utf-8")
        html = html.replace("<head>", "<head>\n" + PRE % theme, 1).replace("</body>", POST[post] + "</body>", 1)
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        target = page
        if crop:  # phone: 390px iframe
            target = Path(tmp) / "phone.html"
            target.write_text(f'<!doctype html><body style="margin:0"><iframe src="page.html" '
                              f'style="width:{crop[0]}px;height:{crop[1]}px;border:0;display:block;margin:0 auto"></iframe></body>')
        png = Path(tmp) / "out.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
                        "--virtual-time-budget=10000", f"--screenshot={png}", target.as_uri()],
                       check=True, capture_output=True, timeout=120)
        if crop:
            # sips crops around the centre, where the iframe sits
            subprocess.run(["sips", "--cropToHeightWidth", str(crop[1]), str(crop[0]), str(png)],
                           check=True, capture_output=True)
        OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy(png, OUT / f"{name}.png")
        print("wrote", OUT / f"{name}.png")


if __name__ == "__main__":
    shot("desktop-light", "light", "plain", (1440, 960))
    shot("desktop-dark", "dark", "plain", (1440, 960))
    shot("benchmark", "light", "benchmark", (1440, 1200))
    shot("mobile", "light", "plain", (600, 1400), crop=(390, 1400))
