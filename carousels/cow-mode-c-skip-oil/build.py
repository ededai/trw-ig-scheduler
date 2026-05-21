"""Mode C — Poster Bold · Cost of Waiting · Skip the oil. Kill the engine.

Renders 6 slides at 1080x1350. Poster Bold = dark bg, hero product photo,
MASSIVE bold sans headline, orange chips, big $ stat callouts.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/assets/newseries-cow-mode-c-2026-05-04-20/slides')
OUT.mkdir(parents=True, exist_ok=True)

SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&display=swap');
* { margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }
body { width:1080px; height:1350px; font-family:'Inter',sans-serif; color:#F2EBDD; background:#0F0F12; overflow:hidden; position:relative; }
.frame { position:absolute; inset:0; padding:60px 64px 80px; display:flex; flex-direction:column; }
.top-bar { display:flex; justify-content:space-between; align-items:center; height:48px; }
.logo { width:56px; height:56px; background:#F2EBDD; border-radius:999px; display:flex; align-items:center; justify-content:center; color:#0F0F12; font-weight:900; font-size:11px; line-height:1; text-align:center; flex-shrink:0; }
.eyebrow-top { display:inline-block; padding:8px 14px; background:#E96A2C; color:#0F0F12; font-size:12px; letter-spacing:2px; font-weight:900; text-transform:uppercase; border-radius:4px; }
.bottom-bar { position:absolute; left:64px; right:64px; bottom:48px; display:flex; justify-content:space-between; align-items:center; font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:800; color:#F2EBDD; }
.headline { font-family:'Inter',sans-serif; font-weight:900; line-height:0.92; letter-spacing:-3px; text-transform:uppercase; }
.accent { color:#E96A2C; }
.body-copy { font-size:22px; line-height:1.45; font-weight:400; color:#F2EBDD; }
.body-copy strong { font-weight:700; }
.eyebrow-section { font-size:13px; letter-spacing:3px; font-weight:800; text-transform:uppercase; color:#E96A2C; margin-bottom:14px; }
.divider { height:1px; background:#F2EBDD; opacity:0.18; margin:24px 0; }
.stat-big { font-family:'Inter',sans-serif; font-weight:900; font-size:140px; line-height:0.85; letter-spacing:-5px; }
"""

LOGO = '<div class="logo"><span>THE<br/>RIGHT<br/>WS</span></div>'

def page(content, footer_left="COST OF WAITING", footer_right="SWIPE →"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{SHARED_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO}<div class="eyebrow-top">COST OF WAITING</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""

# SLIDE 1 — HERO with hero photo
SLIDE1 = page(f"""
<div style="margin-top:24px; height:480px; background:linear-gradient(180deg, rgba(15,15,18,0.30) 0%, rgba(15,15,18,0.45) 60%, rgba(15,15,18,0.92) 100%), url('https://images.unsplash.com/photo-1650179172998-035ba1b497b9?w=1600&q=85') center/cover; border-radius:14px; position:relative;">
  <div style="position:absolute; top:32px; right:32px;"><span class="eyebrow-top" style="background:#0F0F12; color:#E96A2C; border:1px solid #E96A2C;">$50  →  $5,000</span></div>
</div>
<div style="margin-top:36px;">
  <div class="eyebrow-section">PRICE OF SKIPPING SERVICE</div>
  <div class="headline" style="font-size:108px;">Skip<br/>the oil.<br/>Kill the<br/><span class="accent">engine.</span></div>
  <div class="body-copy" style="margin-top:24px; max-width:880px;">
    Old oil is acid. <strong>15,000 km of skipped service</strong> turns lubricant into sludge. The engine eats itself from the inside out.
  </div>
</div>
""", footer_right="01 / 06  →")

# SLIDE 2 — TIMELINE OF SKIPS
SLIDE2 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:24px;">
  <div class="eyebrow-section">WHAT EACH SKIP COSTS</div>
  <div class="headline" style="font-size:90px;">Each cycle<br/>matters.</div>
  <div style="margin-top:18px; display:flex; flex-direction:column; gap:18px;">
    <div style="display:grid; grid-template-columns: 220px 1fr; gap:24px; align-items:center; padding:20px 24px; background:#1A1A1F; border-radius:12px;">
      <div class="stat-big" style="font-size:64px; color:#F2EBDD; white-space:nowrap;">SKIP 1</div>
      <div><div style="font-weight:800; font-size:18px; color:#E96A2C; letter-spacing:1.5px; text-transform:uppercase;">ADDITIVES GONE</div><div class="body-copy" style="margin-top:4px;">Detergents and antiwear additives are spent.</div></div>
    </div>
    <div style="display:grid; grid-template-columns: 220px 1fr; gap:24px; align-items:center; padding:20px 24px; background:#1A1A1F; border-radius:12px;">
      <div class="stat-big" style="font-size:64px; color:#F2EBDD; white-space:nowrap;">SKIP 2</div>
      <div><div style="font-weight:800; font-size:18px; color:#E96A2C; letter-spacing:1.5px; text-transform:uppercase;">METAL ON METAL</div><div class="body-copy" style="margin-top:4px;">Bearings start scoring. Filings appear in the pan.</div></div>
    </div>
    <div style="display:grid; grid-template-columns: 220px 1fr; gap:24px; align-items:center; padding:20px 24px; background:#E96A2C; color:#0F0F12; border-radius:12px;">
      <div class="stat-big" style="font-size:64px; color:#0F0F12; white-space:nowrap;">SKIP 3</div>
      <div><div style="font-weight:900; font-size:18px; color:#0F0F12; letter-spacing:1.5px; text-transform:uppercase;">SEIZED</div><div class="body-copy" style="margin-top:4px; color:#0F0F12;"><strong>Engine locks. Tow + rebuild. $8,000+.</strong></div></div>
    </div>
  </div>
</div>
""", footer_right="02 / 06  →")

# SLIDE 3 — THE NUMBERS
SLIDE3 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:30px;">
  <div class="eyebrow-section">THE COST CURVE</div>
  <div class="headline" style="font-size:80px;">$50 service.<br/>$5,000<br/><span class="accent">rebuild.</span></div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:14px;">
    <div style="background:#1A1A1F; border-radius:12px; padding:28px;">
      <div style="font-size:13px; letter-spacing:2px; font-weight:800; text-transform:uppercase; color:#F2EBDD; opacity:0.7;">ON SCHEDULE</div>
      <div class="stat-big" style="margin-top:8px; color:#F2EBDD;">$50</div>
      <div class="body-copy" style="margin-top:8px; font-size:18px; opacity:0.85;">Oil + filter every 7,500 km.</div>
    </div>
    <div style="background:#E96A2C; color:#0F0F12; border-radius:12px; padding:28px;">
      <div style="font-size:13px; letter-spacing:2px; font-weight:900; text-transform:uppercase; color:#0F0F12;">SKIPPED TWICE</div>
      <div class="stat-big" style="margin-top:8px; color:#0F0F12;">$5,000<span style="font-size:60px;">+</span></div>
      <div class="body-copy" style="margin-top:8px; font-size:18px; color:#0F0F12;">Engine rebuild. Maybe a new block.</div>
    </div>
  </div>
  <div class="body-copy" style="text-align:center; opacity:0.85; font-style:italic;">100x cost gap. Same car. Same engine. Same owner.</div>
</div>
""", footer_right="03 / 06  →")

# SLIDE 4 — DIAGNOSTIC SIGNS
SLIDE4 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:24px;">
  <div class="eyebrow-section">SIGNS YOU'RE OVERDUE</div>
  <div class="headline" style="font-size:84px;">Black,<br/>thin,<br/><span class="accent">burning.</span></div>
  <div style="display:flex; flex-direction:column; gap:14px; margin-top:14px;">
    <div style="display:flex; gap:18px; align-items:flex-start;"><div style="flex-shrink:0; width:48px; height:48px; background:#E96A2C; color:#0F0F12; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">1</div><div class="body-copy"><strong>Dipstick comes out black.</strong> Oil should be golden-amber. Coal-black means sludge.</div></div>
    <div style="display:flex; gap:18px; align-items:flex-start;"><div style="flex-shrink:0; width:48px; height:48px; background:#E96A2C; color:#0F0F12; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">2</div><div class="body-copy"><strong>Engine ticks at idle.</strong> The lifters aren't getting clean oil.</div></div>
    <div style="display:flex; gap:18px; align-items:flex-start;"><div style="flex-shrink:0; width:48px; height:48px; background:#E96A2C; color:#0F0F12; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">3</div><div class="body-copy"><strong>Burning smell after a long drive.</strong> Old oil's flash point is dropping.</div></div>
    <div style="display:flex; gap:18px; align-items:flex-start;"><div style="flex-shrink:0; width:48px; height:48px; background:#E96A2C; color:#0F0F12; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">4</div><div class="body-copy"><strong>Service sticker is older than your last birthday.</strong> If you can't remember, it's overdue.</div></div>
  </div>
</div>
""", footer_right="04 / 06  →")

# SLIDE 5 — THE RULE
SLIDE5 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:24px;">
  <div class="eyebrow-section">THE RULE</div>
  <div class="headline" style="font-size:120px;">7,500<br/>km<br/><span style="font-size:60px; font-weight:700; color:#F2EBDD; opacity:0.7; letter-spacing:0; text-transform:none; font-style:italic;">or every 6 months.</span></div>
  <div class="divider"></div>
  <div class="body-copy" style="max-width:880px;">
    Whichever comes first. Manufacturers publish service intervals because oils, belts and fluids degrade on a schedule.
  </div>
  <div class="body-copy" style="max-width:880px;">
    <strong>Forget them, and the cost curve goes vertical.</strong>
  </div>
</div>
""", footer_right="05 / 06  →")

# SLIDE 6 — CTA
SLIDE6 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section">BOOK YOUR NEXT OIL CHANGE</div>
  <div class="headline" style="font-size:108px;">Service<br/>on time.<br/><span class="accent">Pay once.</span></div>
  <div class="divider"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;">
    <div style="width:54px; height:54px; background:#E96A2C; border-radius:999px; color:#0F0F12; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">W</div>
    <div><div style="font-weight:900; font-size:22px;">WhatsApp</div><div class="body-copy">+65 9855 8423</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;">
    <div style="width:54px; height:54px; background:#E96A2C; border-radius:999px; color:#0F0F12; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">📍</div>
    <div><div style="font-weight:900; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;">
    <div style="width:54px; height:54px; background:#E96A2C; border-radius:999px; color:#0F0F12; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">↗</div>
    <div><div style="font-weight:900; font-size:22px;">therightworkshop.com</div><div class="body-copy">Link in bio</div></div>
  </div>
</div>
""", footer_left="THE RIGHT WORKSHOP", footer_right="HONEST BY DESIGN")

SLIDES = [
    ("slide_1.png", SLIDE1),
    ("slide_2.png", SLIDE2),
    ("slide_3.png", SLIDE3),
    ("slide_4.png", SLIDE4),
    ("slide_5.png", SLIDE5),
    ("slide_6.png", SLIDE6),
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
