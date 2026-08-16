"""Mode D — Polaroid Zine · Cost of Waiting · I waited one year too long.

Renders 7 slides at 1080x1350. Polaroid Zine = cream bg, angled polaroid photos,
yellow sticky notes with handwritten font, serif headline, scrapbook layout.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/assets/newseries-cow-mode-d-2026-05-06-20/slides')
OUT.mkdir(parents=True, exist_ok=True)

SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Caveat:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;700&display=swap');
* { margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }
body { width:1080px; height:1350px; font-family:'Inter',sans-serif; color:#1A1A1A; background:#EDE3CD; overflow:hidden; position:relative; }
.frame { position:absolute; inset:0; padding:60px 64px 80px; display:flex; flex-direction:column; }
.top-bar { display:flex; justify-content:space-between; align-items:center; height:48px; }
.logo { width:56px; height:56px; background:#1A1A1A; border-radius:999px; display:flex; align-items:center; justify-content:center; color:#EDE3CD; font-weight:800; font-size:11px; line-height:1; text-align:center; flex-shrink:0; }
.eyebrow-top { font-size:13px; letter-spacing:3px; font-weight:700; color:#1A1A1A; text-transform:uppercase; }
.bottom-bar { position:absolute; left:64px; right:64px; bottom:48px; display:flex; justify-content:space-between; align-items:center; font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:700; color:#1A1A1A; }
.headline { font-family:'Playfair Display', serif; font-weight:900; line-height:0.95; letter-spacing:-1px; }
.accent { color:#C73E2C; font-style:italic; }
.body-mono { font-family:'JetBrains Mono', monospace; font-size:19px; line-height:1.55; font-weight:400; color:#1A1A1A; }
.body-mono strong { font-weight:700; }
.eyebrow-section { font-size:13px; letter-spacing:3px; font-weight:700; text-transform:uppercase; color:#C73E2C; margin-bottom:14px; }
.handwriting { font-family:'Caveat', cursive; font-size:26px; line-height:1.35; font-weight:500; color:#1A1A1A; }
.polaroid { background:#FFFFFF; padding:14px 14px 56px; border-radius:2px; box-shadow:0 18px 36px rgba(0,0,0,0.18), 0 4px 10px rgba(0,0,0,0.10); position:relative; }
.polaroid-photo { width:100%; height:380px; background-size:cover; background-position:center; }
.polaroid-caption { font-family:'Caveat', cursive; font-size:22px; color:#1A1A1A; text-align:center; padding-top:12px; }
.sticky { background:#F4D960; padding:24px 26px; border-radius:2px; box-shadow:0 10px 22px rgba(0,0,0,0.14); position:relative; transform:rotate(2deg); }
.sticky::before { content:""; position:absolute; top:-10px; left:50%; transform:translateX(-50%) rotate(-3deg); width:90px; height:24px; background:rgba(220,200,150,0.55); border-radius:2px; }
"""

LOGO = '<div class="logo"><span>THE<br/>RIGHT<br/>WS</span></div>'
PHOTO = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=85"  # car at night

def page(content, footer_left="THE RIGHT WORKSHOP", footer_right="READ IT →"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{SHARED_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO}<div class="eyebrow-top">COST OF WAITING</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""

# SLIDE 1 — HERO with polaroid + sticky
SLIDE1 = page(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:flex-start;">
  <div style="position:relative; height:480px;">
    <div class="polaroid" style="width:560px; transform:rotate(-3deg); position:absolute; left:0; top:0;">
      <div class="polaroid-photo" style="background-image:url('{PHOTO}');"></div>
      <div class="polaroid-caption">Stranded · 7 am · void deck stack</div>
    </div>
    <div class="sticky" style="width:300px; position:absolute; right:8px; top:120px;">
      <div class="handwriting">$180 service.<br/>Skipped twice.<br/>Now $3,400.<br/><br/><strong>Lesson learned.</strong></div>
    </div>
  </div>
  <div style="margin-top:36px;">
    <div class="eyebrow-section">GUEST DIARY · LAST TUESDAY</div>
    <div class="headline" style="font-size:78px;">I waited <span class="accent">one year</span> too long.</div>
    <div class="body-mono" style="margin-top:18px;">
      The brake squeal started in March. I told myself "next service." Eight months later, the disc warped. New rotor, new pad, new caliper. <strong>Could have been $180. Was $1,500.</strong>
    </div>
  </div>
</div>
""", footer_right="01 / 07  →")

# SLIDE 2 — TIMELINE polaroid grid
SLIDE2 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column;">
  <div class="eyebrow-section">THE EIGHT MONTHS I IGNORED IT</div>
  <div class="headline" style="font-size:62px; margin-bottom:30px;">A small noise<br/>became a <span class="accent">big bill.</span></div>
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:18px;">
    <div class="polaroid" style="transform:rotate(-2deg); padding:10px 10px 36px;">
      <div style="background:#1A1A1A; height:200px; display:flex; align-items:center; justify-content:center; color:#EDE3CD; font-family:'Caveat',cursive; font-size:30px; padding:14px; text-align:center;">first squeal</div>
      <div style="font-family:'Caveat',cursive; font-size:18px; text-align:center; padding-top:10px;">March · ignored it</div>
    </div>
    <div class="polaroid" style="transform:rotate(1.5deg); padding:10px 10px 36px;">
      <div style="background:#1A1A1A; height:200px; display:flex; align-items:center; justify-content:center; color:#EDE3CD; font-family:'Caveat',cursive; font-size:30px; padding:14px; text-align:center;">it got louder</div>
      <div style="font-family:'Caveat',cursive; font-size:18px; text-align:center; padding-top:10px;">July · still ignored</div>
    </div>
    <div class="polaroid" style="transform:rotate(-1deg); padding:10px 10px 36px;">
      <div style="background:#C73E2C; height:200px; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-family:'Caveat',cursive; font-size:30px; padding:14px; text-align:center;">grinding now</div>
      <div style="font-family:'Caveat',cursive; font-size:18px; text-align:center; padding-top:10px;">Nov · stranded</div>
    </div>
  </div>
  <div class="body-mono" style="margin-top:30px;">
    Brake parts wear in stages. <strong>Catch the squeal, save the rotor.</strong> Catch the grinding, you're already paying for the caliper too.
  </div>
</div>
""", footer_right="02 / 07  →")

# SLIDE 3 — STICKY NOTE OF DAMAGE
SLIDE3 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:32px;">
  <div class="eyebrow-section">THE INVOICE I DID NOT WANT</div>
  <div class="headline" style="font-size:72px;">What waiting<br/><span class="accent">actually cost.</span></div>
  <div class="sticky" style="width:560px; transform:rotate(-1deg); padding:32px 36px;">
    <div class="handwriting" style="font-size:30px;">
      <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #1A1A1A; padding-bottom:8px; margin-bottom:8px;"><span>Brake pads</span><span>$180</span></div>
      <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #1A1A1A; padding-bottom:8px; margin-bottom:8px;"><span>Rotor (warped)</span><span>$420</span></div>
      <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #1A1A1A; padding-bottom:8px; margin-bottom:8px;"><span>Caliper (seized)</span><span>$680</span></div>
      <div style="display:flex; justify-content:space-between; border-bottom:1px dashed #1A1A1A; padding-bottom:8px; margin-bottom:8px;"><span>Tow + diag</span><span>$220</span></div>
      <div style="display:flex; justify-content:space-between; padding-top:8px; font-weight:700;"><span>TOTAL</span><span>$1,500</span></div>
    </div>
  </div>
  <div class="body-mono">
    The squeal in March was a $180 problem. <strong>I made it a $1,500 problem.</strong>
  </div>
</div>
""", footer_right="03 / 07  →")

# SLIDE 4 — THINGS I HEARD AND IGNORED
SLIDE4 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:22px;">
  <div class="eyebrow-section">FOUR THINGS I HEARD · IGNORED ALL OF THEM</div>
  <div class="headline" style="font-size:58px;">Small signals.<br/><span class="accent">Big bills.</span></div>
  <div style="display:flex; flex-direction:column; gap:14px; margin-top:8px;">
    <div style="display:grid; grid-template-columns: 56px 1fr; gap:18px; align-items:flex-start;"><div class="handwriting" style="font-size:38px; color:#C73E2C; font-weight:700;">1.</div><div class="body-mono"><strong>A high-pitched squeal at low speed.</strong> Pad wear indicator hitting the rotor.</div></div>
    <div style="display:grid; grid-template-columns: 56px 1fr; gap:18px; align-items:flex-start;"><div class="handwriting" style="font-size:38px; color:#C73E2C; font-weight:700;">2.</div><div class="body-mono"><strong>A pulse through the pedal.</strong> Rotor warping from heat cycling.</div></div>
    <div style="display:grid; grid-template-columns: 56px 1fr; gap:18px; align-items:flex-start;"><div class="handwriting" style="font-size:38px; color:#C73E2C; font-weight:700;">3.</div><div class="body-mono"><strong>One side pulling harder.</strong> Caliper sticking. Heat building on one wheel.</div></div>
    <div style="display:grid; grid-template-columns: 56px 1fr; gap:18px; align-items:flex-start;"><div class="handwriting" style="font-size:38px; color:#C73E2C; font-weight:700;">4.</div><div class="body-mono"><strong>A grinding I could feel in my teeth.</strong> Metal on metal. Past the point of pads.</div></div>
  </div>
</div>
""", footer_right="04 / 07  →")

# SLIDE 5 — IF I COULD DO IT AGAIN
SLIDE5 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:30px;">
  <div class="eyebrow-section">WHAT I'D DO DIFFERENTLY</div>
  <div class="headline" style="font-size:72px;">Book it<br/>on the<br/><span class="accent">first squeal.</span></div>
  <div class="sticky" style="transform:rotate(1.5deg); width:600px;">
    <div class="handwriting" style="font-size:28px;">If it squeals once,<br/>book it that week.<br/><br/>If it pulses, book it tomorrow.<br/><br/><strong>If it grinds — drive nowhere<br/>except a workshop.</strong></div>
  </div>
  <div class="body-mono">
    Brakes do not get better on their own. The squeal is the cheapest warning you will ever get.
  </div>
</div>
""", footer_right="05 / 07  →")

# SLIDE 6 — THE LESSON
SLIDE6 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:22px;">
  <div class="eyebrow-section">THE LESSON</div>
  <div class="headline" style="font-size:96px;">Waiting<br/>is the most<br/>expensive<br/><span class="accent">repair.</span></div>
  <div class="body-mono" style="max-width:880px;">
    Every part of a car wears in steps. The cheapest step is the first one. <strong>Catch it there.</strong>
  </div>
  <div class="body-mono" style="max-width:880px; font-style:italic; opacity:0.85;">
    — A guest diary from a customer who said we could share his story so someone else doesn't repeat it.
  </div>
</div>
""", footer_right="06 / 07  →")

# SLIDE 7 — CTA
SLIDE7 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section">BRING IT IN ON THE FIRST SIGNAL</div>
  <div class="headline" style="font-size:88px;">If it squeals,<br/><span class="accent">come straight in.</span></div>
  <div style="height:1px; background:#1A1A1A; opacity:0.2; margin:30px 0 20px;"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EDE3CD; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:22px;">W</div>
    <div><div style="font-weight:800; font-size:22px;">WhatsApp</div><div class="body-mono">+65 8952 1688</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EDE3CD; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">📍</div>
    <div><div style="font-weight:800; font-size:22px;">Workshop</div><div class="body-mono">Autobay @ Kaki Bukit, #02-61</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EDE3CD; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">↗</div>
    <div><div style="font-weight:800; font-size:22px;">therightworkshop.com</div><div class="body-mono">Link in bio</div></div>
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
    ("slide_7.png", SLIDE7),
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
