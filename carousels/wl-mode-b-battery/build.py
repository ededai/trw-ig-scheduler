"""Prototype carousel render — Warning Light Decoded · Mode B (Cream Magazine) · Battery Light.

Renders 5 slides at 1080x1350 using Playwright. Each slide is a different "view"
within the same Cream Magazine aesthetic (cream bg, serif headline with red accent,
TRW logo top-left, eyebrow top-right).

Slides:
  1. Hero / hook — "Battery light on. Heart sinks." (full-bleed photo)
  2. Diagnosis card — "It's almost never the battery." (info layout)
  3. Urgency timeline — "30 min OK. 60 min stalling." (timeline)
  4. Cost split — "$300 now vs $1,500 stranded." (numbers)
  5. CTA — universal TRW signoff
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
OUT = ROOT.parent.parent / "assets/newseries-wl-mode-b-2026-05-02-11/slides"
OUT.mkdir(parents=True, exist_ok=True)

# Shared Cream Magazine CSS (Mode B)
SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Inter:wght@400;500;600;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; }
body {
  width: 1080px; height: 1350px;
  background: #EFE6D4;
  font-family: 'Inter', sans-serif;
  color: #1A1A1A;
  overflow: hidden;
  position: relative;
}
.frame { position: absolute; inset: 0; padding: 60px 64px; display: flex; flex-direction: column; }
.top-bar { display: flex; justify-content: space-between; align-items: center; height: 48px; }
.logo { width: 56px; height: 56px; background: #1A1A1A; border-radius: 999px; display: flex; align-items: center; justify-content: center; color: #EFE6D4; font-weight: 700; font-size: 11px; letter-spacing: 0.5px; line-height: 1; text-align: center; flex-shrink: 0; }
.logo span { display: block; }
.eyebrow-top { font-size: 13px; letter-spacing: 3px; font-weight: 600; color: #1A1A1A; text-transform: uppercase; }
.bottom-bar { position: absolute; left: 64px; right: 64px; bottom: 48px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; color: #1A1A1A; }
.accent { color: #C73E2C; }
.headline { font-family: 'Playfair Display', serif; font-weight: 900; font-size: 86px; line-height: 0.95; letter-spacing: -2px; }
.body-copy { font-family: 'Inter', sans-serif; font-size: 22px; line-height: 1.45; color: #1A1A1A; font-weight: 400; }
.body-copy strong { font-weight: 600; }
.eyebrow-section { font-size: 13px; letter-spacing: 3px; font-weight: 700; text-transform: uppercase; color: #1A1A1A; margin-bottom: 18px; }
.divider { height: 1px; background: #1A1A1A; opacity: 0.2; margin: 22px 0; }
.chip { display: inline-block; padding: 8px 14px; background: #C73E2C; color: #EFE6D4; font-size: 12px; letter-spacing: 2px; font-weight: 700; text-transform: uppercase; border-radius: 4px; }
"""

LOGO = '<div class="logo"><span>THE<br/>RIGHT<br/>WORKSHOP</span></div>'

def page(eyebrow_top, body_html, footer_left="DECODED BY THE RIGHT WORKSHOP", footer_right="SWIPE →"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{SHARED_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO}<div class="eyebrow-top">{eyebrow_top}</div></div>
  {body_html}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""

# ============ SLIDE 1 — HERO (full photo + headline overlay) ============
SLIDE1 = page(
    eyebrow_top="WARNING LIGHT DECODED",
    body_html="""
<div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end; margin-top: 40px;">
  <div style="background: linear-gradient(180deg, transparent 0%, rgba(20,20,20,0.15) 25%, #1f1916 90%), url('https://images.unsplash.com/photo-1597386601945-8980df52c3dc?w=1600&q=85') center/cover; height: 720px; border-radius: 18px; position: relative; padding: 48px; display:flex; flex-direction:column; justify-content:flex-end;">
    <div style="position:absolute; top:32px; right:32px;"><span class="chip" style="background:#C73E2C;">HIGH SEVERITY</span></div>
    <div style="color:#EFE6D4;">
      <div class="eyebrow-section" style="color:#EFE6D4; opacity:0.85; margin-bottom:14px;">BATTERY LIGHT · DECODED</div>
      <div class="headline" style="font-size:78px; color:#EFE6D4; letter-spacing:-1.5px;">Battery light on.<br/><span style="color:#F4A93A;">Heart sinks.</span></div>
    </div>
  </div>
  <div class="body-copy" style="margin-top:28px; max-width:880px;">
    It is rarely the battery itself. Most of the time the alternator stopped charging — and your battery has been carrying the car alone.
  </div>
</div>
""",
    footer_right="01 / 05  →"
)

# ============ SLIDE 2 — DIAGNOSIS (info card with breakdown) ============
SLIDE2 = page(
    eyebrow_top="WARNING LIGHT DECODED",
    body_html="""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 30px;">
  <div class="eyebrow-section">WHAT IT ACTUALLY MEANS</div>
  <div class="headline" style="font-size:92px;">It's not the<br/><span class="accent">battery.</span></div>
  <div class="divider"></div>
  <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 18px;">
    <div>
      <div style="font-family:'Playfair Display',serif; font-size:48px; font-weight:700; color:#C73E2C; line-height:1;">9 / 10</div>
      <div class="body-copy" style="margin-top:10px;">It's the alternator. The battery just delivers what the alternator made.</div>
    </div>
    <div>
      <div style="font-family:'Playfair Display',serif; font-size:48px; font-weight:700; color:#1A1A1A; line-height:1;">When it dies</div>
      <div class="body-copy" style="margin-top:10px;">Power steering goes heavy, dashboard dims, then everything cuts.</div>
    </div>
  </div>
  <div class="body-copy" style="margin-top:36px;"><strong>The light is the warning.</strong> The stall is the verdict.</div>
</div>
""",
    footer_right="02 / 05  →"
)

# ============ SLIDE 3 — URGENCY TIMELINE ============
SLIDE3 = page(
    eyebrow_top="WARNING LIGHT DECODED",
    body_html="""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 30px;">
  <div class="eyebrow-section">HOW LONG YOU HAVE</div>
  <div class="headline" style="font-size:80px; margin-bottom: 36px;">Drive less.<br/>Drive home.<br/><span class="accent">Don't drive far.</span></div>

  <div style="background:#1A1A1A; border-radius:14px; padding:32px; color:#EFE6D4;">
    <div style="display:grid; grid-template-columns: 130px 1fr; gap:20px; align-items:center; margin-bottom:22px;">
      <div style="font-family:'Playfair Display',serif; font-size:42px; font-weight:900; color:#F4A93A; white-space:nowrap;">0–30</div>
      <div><div style="font-weight:700; font-size:18px; letter-spacing:1px; text-transform:uppercase; color:#F4A93A;">MIN</div><div style="margin-top:4px; font-size:20px;">Battery alone can carry the car. You may still make it home.</div></div>
    </div>
    <div style="display:grid; grid-template-columns: 130px 1fr; gap:20px; align-items:center; margin-bottom:22px;">
      <div style="font-family:'Playfair Display',serif; font-size:42px; font-weight:900; color:#EFE6D4; white-space:nowrap;">30–60</div>
      <div><div style="font-weight:700; font-size:18px; letter-spacing:1px; text-transform:uppercase;">MIN</div><div style="margin-top:4px; font-size:20px;">Power steering goes. Dashboard dims. Don't merge onto the PIE.</div></div>
    </div>
    <div style="display:grid; grid-template-columns: 130px 1fr; gap:20px; align-items:center;">
      <div style="font-family:'Playfair Display',serif; font-size:42px; font-weight:900; color:#C73E2C; white-space:nowrap;">60+</div>
      <div><div style="font-weight:700; font-size:18px; letter-spacing:1px; text-transform:uppercase; color:#C73E2C;">MIN</div><div style="margin-top:4px; font-size:20px;">Engine cuts mid-traffic. Stranded. Tow required.</div></div>
    </div>
  </div>
</div>
""",
    footer_right="03 / 05  →"
)

# ============ SLIDE 4 — COST SPLIT ============
SLIDE4 = page(
    eyebrow_top="WARNING LIGHT DECODED",
    body_html="""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 30px;">
  <div class="eyebrow-section">PRICE OF NOT WAITING</div>
  <div class="headline" style="font-size:76px; margin-bottom: 32px;">Catch it now,<br/>or pay later.</div>

  <div style="display:grid; grid-template-columns: 1fr 1fr; gap:24px;">
    <div style="background:#FFFFFF; border:1.5px solid #1A1A1A; border-radius:14px; padding:32px;">
      <div style="font-size:13px; letter-spacing:2px; font-weight:700; text-transform:uppercase; color:#1A1A1A;">CATCH IT NOW</div>
      <div style="font-family:'Playfair Display',serif; font-size:88px; font-weight:900; color:#1A1A1A; line-height:1; margin:12px 0;">$300</div>
      <div class="body-copy" style="font-size:18px;">Alternator replaced. Battery tested. Belt checked. Drive home the same day.</div>
    </div>
    <div style="background:#1A1A1A; border-radius:14px; padding:32px; color:#EFE6D4;">
      <div style="font-size:13px; letter-spacing:2px; font-weight:700; text-transform:uppercase; color:#F4A93A;">STRANDED</div>
      <div style="font-family:'Playfair Display',serif; font-size:88px; font-weight:900; color:#EFE6D4; line-height:1; margin:12px 0;">$1,500<span style="font-size:32px; font-weight:400;">+</span></div>
      <div class="body-copy" style="font-size:18px; color:#EFE6D4;">Tow + alternator + new battery + missed appointments + the bad afternoon.</div>
    </div>
  </div>
  <div class="body-copy" style="margin-top:32px; font-style: italic;">Free OBD scan + alternator load test when you book.</div>
</div>
""",
    footer_right="04 / 05  →"
)

# ============ SLIDE 5 — CTA ============
SLIDE5 = page(
    eyebrow_top="WARNING LIGHT DECODED",
    body_html="""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 20px;">
  <div class="eyebrow-section">SAVE THIS · BOOK WHEN IT HAPPENS</div>
  <div class="headline" style="font-size:96px;">If the battery<br/>light comes on,<br/><span class="accent">come straight in.</span></div>

  <div class="divider" style="margin:36px 0 28px;"></div>

  <div style="display:grid; grid-template-columns: auto 1fr; gap:18px; align-items:center; margin-bottom:20px;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:22px;">W</div>
    <div><div style="font-weight:700; font-size:22px;">WhatsApp</div><div class="body-copy">+65 8952 1688</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:18px; align-items:center; margin-bottom:20px;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:22px;">📍</div>
    <div><div style="font-weight:700; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:18px; align-items:center;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:18px;">↗</div>
    <div><div style="font-weight:700; font-size:22px;">Read the full guide</div><div class="body-copy">therightworkshop.com / link in bio</div></div>
  </div>
</div>
""",
    footer_left="THE RIGHT WORKSHOP",
    footer_right="HONEST BY DESIGN"
)


SLIDES = [
    ("slide_1.png", SLIDE1),
    ("slide_2.png", SLIDE2),
    ("slide_3.png", SLIDE3),
    ("slide_4.png", SLIDE4),
    ("slide_5.png", SLIDE5),
]


async def render_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        page = await ctx.new_page()
        for filename, html in SLIDES:
            await page.set_content(html, wait_until="networkidle")
            await page.wait_for_timeout(400)
            out_path = OUT / filename
            await page.screenshot(path=str(out_path), full_page=False, omit_background=False)
            print(f"  rendered {out_path}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(render_all())
    print("done.")
