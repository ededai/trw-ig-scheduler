"""Mode A — Editorial Dark · Straight Talk · Ask the three questions.

Renders 6 slides at 1080x1350. Editorial Dark = full-bleed warm dark photo,
white sans-serif type, orange accent word, eyebrow chips, "HONEST BY DESIGN".
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/assets/newseries-st-mode-a-2026-05-02-15/slides')
OUT.mkdir(parents=True, exist_ok=True)

# Mode A — Editorial Dark CSS
SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }
body { width:1080px; height:1350px; font-family:'Inter',sans-serif; color:#F2EBDD; background:#1A1410; overflow:hidden; position:relative; }
.bg { position:absolute; inset:0; background-size:cover; background-position:center; }
.overlay { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,0.50) 0%, rgba(20,16,12,0.30) 35%, rgba(20,16,12,0.85) 75%, #1A1410 100%); }
.frame { position:absolute; inset:0; padding:60px 64px 80px; display:flex; flex-direction:column; }
.top-bar { display:flex; justify-content:space-between; align-items:center; height:48px; }
.logo { width:56px; height:56px; background:#F2EBDD; border-radius:999px; display:flex; align-items:center; justify-content:center; color:#1A1410; font-weight:800; font-size:11px; line-height:1; text-align:center; flex-shrink:0; }
.eyebrow-top { font-size:13px; letter-spacing:3px; font-weight:700; color:#F2EBDD; text-transform:uppercase; }
.bottom-bar { position:absolute; left:64px; right:64px; bottom:48px; display:flex; justify-content:space-between; align-items:center; font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:700; color:#F2EBDD; }
.accent { color:#F4A93A; }
.headline { font-family:'Inter',sans-serif; font-weight:900; line-height:0.95; letter-spacing:-2px; }
.body-copy { font-size:22px; line-height:1.45; font-weight:400; color:#F2EBDD; }
.body-copy strong { font-weight:700; }
.eyebrow-section { font-size:13px; letter-spacing:3px; font-weight:800; text-transform:uppercase; color:#F4A93A; }
.chip { display:inline-block; padding:8px 14px; background:#F4A93A; color:#1A1410; font-size:12px; letter-spacing:2px; font-weight:800; text-transform:uppercase; border-radius:4px; }
.divider { height:1px; background:#F2EBDD; opacity:0.25; margin:24px 0; }
.q-num { font-family:'Inter',sans-serif; font-size:140px; font-weight:900; line-height:0.85; color:#F4A93A; letter-spacing:-4px; }
"""

LOGO = '<div class="logo"><span>THE<br/>RIGHT<br/>WS</span></div>'

# Background photo — workshop with mechanic
BG_PHOTO = "https://images.unsplash.com/photo-1676018366904-c083ed678e60?w=1600&q=85"

def page(content_html, footer_left="HONEST BY DESIGN", footer_right="SWIPE →", with_bg=True):
    bg_html = f'<div class="bg" style="background-image:url(\'{BG_PHOTO}\');"></div><div class="overlay"></div>' if with_bg else ''
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{SHARED_CSS}</style></head><body>
{bg_html}
<div class="frame">
  <div class="top-bar">{LOGO}<div class="eyebrow-top">STRAIGHT TALK</div></div>
  {content_html}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""

# SLIDE 1 — HERO
SLIDE1 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end; padding-bottom:24px;">
  <div style="margin-bottom:16px;"><span class="chip">3 QUESTIONS</span> <span style="font-size:13px; letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-left:8px;">BEFORE YOU PAY YES</span></div>
  <div class="headline" style="font-size:104px;">Ask the<br/><span class="accent">three</span><br/>questions.</div>
  <div class="body-copy" style="margin-top:28px; max-width:880px;">
    "Show me the part." "Show me the spec." "Show me the price." <strong>Honest workshops answer all three.</strong> Upsell shops change the topic.
  </div>
</div>
""", footer_right="01 / 06  →")

# SLIDE 2 — Q1
SLIDE2 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:28px;">
  <div class="eyebrow-section">QUESTION ONE</div>
  <div style="display:grid; grid-template-columns: 200px 1fr; gap:36px; align-items:center;">
    <div class="q-num">01</div>
    <div class="headline" style="font-size:78px;">Show me<br/>the <span class="accent">part.</span></div>
  </div>
  <div class="body-copy" style="max-width:880px; margin-top:8px;">
    The old part out. The new part in. <strong>Side by side, on the bench.</strong> If they cannot show it, they did not change it.
  </div>
  <div class="divider"></div>
  <div class="body-copy" style="font-style:italic; opacity:0.85;">Watch for: "we already disposed of it."</div>
</div>
""", footer_right="02 / 06  →")

# SLIDE 3 — Q2
SLIDE3 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:28px;">
  <div class="eyebrow-section">QUESTION TWO</div>
  <div style="display:grid; grid-template-columns: 200px 1fr; gap:36px; align-items:center;">
    <div class="q-num">02</div>
    <div class="headline" style="font-size:78px;">Show me<br/>the <span class="accent">spec.</span></div>
  </div>
  <div class="body-copy" style="max-width:880px; margin-top:8px;">
    OEM? Aftermarket? Brand? Grade? <strong>Every part has a spec sheet.</strong> An honest mechanic talks brand and grade — not just "good one" or "original."
  </div>
  <div class="divider"></div>
  <div class="body-copy" style="font-style:italic; opacity:0.85;">Watch for: "all the same lah."</div>
</div>
""", footer_right="03 / 06  →")

# SLIDE 4 — Q3
SLIDE4 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:28px;">
  <div class="eyebrow-section">QUESTION THREE</div>
  <div style="display:grid; grid-template-columns: 200px 1fr; gap:36px; align-items:center;">
    <div class="q-num">03</div>
    <div class="headline" style="font-size:78px;">Show me<br/>the <span class="accent">price.</span></div>
  </div>
  <div class="body-copy" style="max-width:880px; margin-top:8px;">
    Itemised. <strong>Parts vs labour vs consumables.</strong> A real quote breaks it down. A fishy quote bundles everything into one round number.
  </div>
  <div class="divider"></div>
  <div class="body-copy" style="font-style:italic; opacity:0.85;">Watch for: "trust me, fair price."</div>
</div>
""", footer_right="04 / 06  →")

# SLIDE 5 — THE TELL
SLIDE5 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
  <div class="eyebrow-section">THE TELL</div>
  <div class="headline" style="font-size:88px; margin-top:16px;">If they dodge<br/>any of the three<br/>— <span class="accent">walk away.</span></div>
  <div class="divider"></div>
  <div class="body-copy" style="max-width:880px;">
    A workshop that cannot show the part, the spec, and the price is not a workshop. It is a sales floor with a hoist.
  </div>
  <div class="body-copy" style="margin-top:24px; max-width:880px;">
    <strong>Honest workshops welcome the questions.</strong> They wrote them down before you walked in.
  </div>
</div>
""", footer_right="05 / 06  →")

# SLIDE 6 — CTA
SLIDE6 = page("""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section">BRING THE QUESTIONS · GET STRAIGHT ANSWERS</div>
  <div class="headline" style="font-size:96px; margin-top:8px;">Honest <br/>by design.</div>
  <div class="divider" style="margin:30px 0 24px;"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;">
    <div style="width:54px; height:54px; background:#F4A93A; border-radius:999px; color:#1A1410; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">W</div>
    <div><div style="font-weight:800; font-size:22px;">WhatsApp</div><div class="body-copy">+65 8952 1688</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;">
    <div style="width:54px; height:54px; background:#F4A93A; border-radius:999px; color:#1A1410; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">📍</div>
    <div><div style="font-weight:800; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;">
    <div style="width:54px; height:54px; background:#F4A93A; border-radius:999px; color:#1A1410; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">↗</div>
    <div><div style="font-weight:800; font-size:22px;">therightworkshop.com</div><div class="body-copy">Link in bio for the full guide</div></div>
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
