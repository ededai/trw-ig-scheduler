"""Mode E — Spec Sheet · Warning Light Decoded · ABS off does not mean brakes off.

Renders 7 slides at 1080x1350. Spec Sheet = cream bg, technical diagrams with
letter labels, sans headline, structured data tables. Engineering reference vibe.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/assets/newseries-wl-mode-e-2026-05-08-11/slides')
OUT.mkdir(parents=True, exist_ok=True)

SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');
* { margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }
body { width:1080px; height:1350px; font-family:'Inter',sans-serif; color:#1A1A1A; background:#EFE6D4; overflow:hidden; position:relative; }
.frame { position:absolute; inset:0; padding:60px 64px 80px; display:flex; flex-direction:column; }
.top-bar { display:flex; justify-content:space-between; align-items:center; height:48px; }
.logo { width:56px; height:56px; background:#1A1A1A; border-radius:999px; display:flex; align-items:center; justify-content:center; color:#EFE6D4; font-weight:800; font-size:11px; line-height:1; text-align:center; flex-shrink:0; }
.eyebrow-top { display:inline-block; padding:8px 14px; background:#1A1A1A; color:#EFE6D4; font-size:12px; letter-spacing:2px; font-weight:800; text-transform:uppercase; border-radius:4px; }
.bottom-bar { position:absolute; left:64px; right:64px; bottom:48px; display:flex; justify-content:space-between; align-items:center; font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:800; color:#1A1A1A; }
.headline { font-family:'Inter',sans-serif; font-weight:900; line-height:0.95; letter-spacing:-2px; }
.accent { color:#C73E2C; }
.body-copy { font-size:21px; line-height:1.45; font-weight:400; color:#1A1A1A; }
.body-copy strong { font-weight:700; }
.eyebrow-section { font-size:12px; letter-spacing:2.5px; font-weight:800; text-transform:uppercase; color:#1A1A1A; }
.spec-table { width:100%; border-collapse:collapse; font-family:'JetBrains Mono', monospace; font-size:14px; }
.spec-table th { text-align:left; font-size:11px; letter-spacing:2px; font-weight:800; text-transform:uppercase; color:#1A1A1A; padding:10px 14px; border-bottom:1px solid #1A1A1A; background:#E2D5B9; }
.spec-table td { padding:14px; vertical-align:top; border-bottom:1px solid #C9BB99; line-height:1.5; }
.spec-table td:first-child { font-weight:700; width:48px; background:#1A1A1A; color:#EFE6D4; text-align:center; font-size:18px; }
.label-pin { position:absolute; width:36px; height:36px; background:#C73E2C; color:#EFE6D4; border-radius:6px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px; box-shadow:0 4px 8px rgba(0,0,0,0.3); }
.divider { height:1px; background:#1A1A1A; opacity:0.25; margin:18px 0; }
"""

LOGO = '<div class="logo"><span>THE<br/>RIGHT<br/>WS</span></div>'
DIAG_PHOTO = "https://images.unsplash.com/photo-1761040100230-8c8e6fc64638?w=1600&q=85"  # red brake caliper + rotor closeup

def page(content, footer_left="WARNING LIGHT · DECODED", footer_right="FULL CHAPTER ↗"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{SHARED_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO}<div class="eyebrow-top">WARNING LIGHT DECODED</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""

# SLIDE 1 — DIAGRAM + HEADLINE + DATA TABLE
SLIDE1 = page(f"""
<div style="margin-top:24px;">
  <div style="display:flex; gap:18px; font-size:11px; letter-spacing:2px; font-weight:800; text-transform:uppercase; color:#1A1A1A; opacity:0.7; margin-bottom:8px;">
    <span>FILE / WL.ABS.SENSOR</span><span style="opacity:1;">SEVERITY / MEDIUM</span><span>ACTION / DRIVE TO TRW</span><span>DIAGNOSE / OBD + WHEEL</span>
  </div>
  <div style="font-weight:700; font-size:20px;">Anti-lock braking system.</div>
  <div style="margin-top:14px; height:340px; background:url('{DIAG_PHOTO}') center/cover; border-radius:6px; position:relative;">
    <div class="label-pin" style="top:30px; left:50px;">A</div>
    <div style="position:absolute; top:30px; left:96px; padding:4px 10px; background:#1A1A1A; color:#EFE6D4; font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:1.5px; font-weight:700;">WHEEL HUB</div>
    <div class="label-pin" style="top:140px; left:160px;">B</div>
    <div style="position:absolute; top:140px; left:206px; padding:4px 10px; background:#1A1A1A; color:#EFE6D4; font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:1.5px; font-weight:700;">ABS SENSOR</div>
    <div class="label-pin" style="top:80px; right:80px;">C</div>
    <div style="position:absolute; top:80px; right:128px; padding:4px 10px; background:#1A1A1A; color:#EFE6D4; font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:1.5px; font-weight:700;">BRAKE DISC</div>
    <div class="label-pin" style="bottom:60px; right:140px;">D</div>
    <div style="position:absolute; bottom:60px; right:188px; padding:4px 10px; background:#1A1A1A; color:#EFE6D4; font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:1.5px; font-weight:700;">WIRING</div>
  </div>
  <div style="margin-top:30px;">
    <div class="eyebrow-section" style="opacity:0.7; margin-bottom:14px;">DECODED · ANTI-LOCK BRAKING</div>
    <div class="headline" style="font-size:74px;">ABS off does not<br/>mean <span class="accent">brakes off.</span></div>
    <div class="body-copy" style="margin-top:20px; max-width:960px;">
      Brakes still work, but anti-lock is disabled. <strong>Skid risk in wet weather.</strong> Most causes: dirty wheel sensor or a broken wire after a kerb hit.
    </div>
  </div>
</div>
""", footer_right="01 / 07  ↗")

# SLIDE 2 — DATA TABLE (full)
SLIDE2 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:flex-start;">
  <div class="eyebrow-section" style="color:#C73E2C;">SPEC TABLE · WHAT HAPPENS WHEN THE ABS LIGHT IS ON</div>
  <div class="headline" style="font-size:60px; margin-top:14px;">Read the<br/>spec, not<br/>the rumour.</div>
  <table class="spec-table" style="margin-top:32px;">
    <thead><tr><th></th><th>Severity</th><th>Common cause</th><th>Diag. cost</th><th>Fix range</th></tr></thead>
    <tbody>
      <tr><td>A</td><td>Medium<br/>not pull-over</td><td>Dirty wheel<br/>sensor</td><td>$60 to $90<br/>OBD + visual</td><td>$120 to $240<br/>per wheel</td></tr>
      <tr><td>B</td><td>Medium</td><td>Broken sensor<br/>wire (kerb hit)</td><td>$60 to $90</td><td>$180 to $360<br/>incl. wire</td></tr>
      <tr><td>C</td><td>High<br/>diagnose now</td><td>Failed ABS<br/>module</td><td>$90 to $150</td><td>$700 to $1,400<br/>refurb / replace</td></tr>
      <tr><td>D</td><td>Low<br/>nuisance</td><td>Brake fluid<br/>low or air</td><td>Free<br/>visual check</td><td>$80 to $140<br/>flush + bleed</td></tr>
    </tbody>
  </table>
</div>
""", footer_right="02 / 07  ↗")

# SLIDE 3 — DECODE SEVERITY MATRIX
SLIDE3 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:24px;">
  <div class="eyebrow-section" style="color:#C73E2C;">SEVERITY · BY DRIVING CONDITION</div>
  <div class="headline" style="font-size:60px;">Not the same risk<br/>in every <span class="accent">condition.</span></div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:8px;">
    <div style="background:#FFFFFF; border:1.5px solid #1A1A1A; border-radius:8px; padding:24px;"><div class="eyebrow-section" style="color:#C73E2C;">DRY · LOW SPEED</div><div style="font-family:'JetBrains Mono',mono; font-size:42px; font-weight:800; margin-top:8px;">LOW RISK</div><div class="body-copy" style="margin-top:8px; font-size:19px;">Brakes still stop the car. Take it to a workshop within the week.</div></div>
    <div style="background:#FFFFFF; border:1.5px solid #1A1A1A; border-radius:8px; padding:24px;"><div class="eyebrow-section" style="color:#C73E2C;">DRY · EXPRESSWAY</div><div style="font-family:'JetBrains Mono',mono; font-size:42px; font-weight:800; margin-top:8px;">MEDIUM</div><div class="body-copy" style="margin-top:8px; font-size:19px;">Hard braking can lock a wheel. Leave more gap.</div></div>
    <div style="background:#FFFFFF; border:1.5px solid #1A1A1A; border-radius:8px; padding:24px;"><div class="eyebrow-section" style="color:#C73E2C;">WET · LOW SPEED</div><div style="font-family:'JetBrains Mono',mono; font-size:42px; font-weight:800; margin-top:8px;">MEDIUM</div><div class="body-copy" style="margin-top:8px; font-size:19px;">Standing water + locked wheel = slide. Brake gently.</div></div>
    <div style="background:#1A1A1A; color:#EFE6D4; border-radius:8px; padding:24px;"><div class="eyebrow-section" style="color:#F4A93A;">WET · EXPRESSWAY</div><div style="font-family:'JetBrains Mono',mono; font-size:42px; font-weight:800; margin-top:8px; color:#C73E2C;">HIGH</div><div class="body-copy" style="margin-top:8px; font-size:19px; color:#EFE6D4;"><strong>Drive home, then book.</strong> Don't push speeds in rain.</div></div>
  </div>
</div>
""", footer_right="03 / 07  ↗")

# SLIDE 4 — DIAGNOSTIC FLOW
SLIDE4 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:22px;">
  <div class="eyebrow-section" style="color:#C73E2C;">DIAGNOSTIC FLOW · 4 STEPS</div>
  <div class="headline" style="font-size:62px;">How we trace<br/>the <span class="accent">light</span> to a part.</div>
  <div style="font-family:'JetBrains Mono',mono; font-size:18px; line-height:1.7; margin-top:10px;">
    <div style="display:grid; grid-template-columns:60px 1fr; gap:14px; padding:14px 0; border-bottom:1px dashed #1A1A1A;"><div style="font-weight:800; color:#C73E2C;">[1]</div><div><strong>OBD scan.</strong> Pull the fault code. C0035 = front-left sensor. C0040 = front-right. Etc.</div></div>
    <div style="display:grid; grid-template-columns:60px 1fr; gap:14px; padding:14px 0; border-bottom:1px dashed #1A1A1A;"><div style="font-weight:800; color:#C73E2C;">[2]</div><div><strong>Visual check.</strong> Wheel sensor face for road grime. Wiring loom for chafing.</div></div>
    <div style="display:grid; grid-template-columns:60px 1fr; gap:14px; padding:14px 0; border-bottom:1px dashed #1A1A1A;"><div style="font-weight:800; color:#C73E2C;">[3]</div><div><strong>Resistance test.</strong> Measure the sensor coil. Out-of-spec = replace.</div></div>
    <div style="display:grid; grid-template-columns:60px 1fr; gap:14px; padding:14px 0;"><div style="font-weight:800; color:#C73E2C;">[4]</div><div><strong>Road test.</strong> Trigger ABS in a safe spot. Confirm pulsing pedal returns.</div></div>
  </div>
</div>
""", footer_right="04 / 07  ↗")

# SLIDE 5 — DRIVING ADVICE
SLIDE5 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:24px;">
  <div class="eyebrow-section" style="color:#C73E2C;">UNTIL YOU CAN BOOK IT IN</div>
  <div class="headline" style="font-size:80px;">Drive like<br/>you have <span class="accent">no ABS.</span><br/>Because you don't.</div>
  <div class="divider"></div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
    <div><div class="eyebrow-section">DO</div><ul style="margin-top:10px; padding-left:18px;" class="body-copy"><li>Leave more following gap.</li><li>Brake earlier, brake softer.</li><li>Pump pedals on slick surfaces.</li><li>Book diag within the week.</li></ul></div>
    <div><div class="eyebrow-section" style="color:#C73E2C;">DON'T</div><ul style="margin-top:10px; padding-left:18px;" class="body-copy"><li>Slam-brake on the expressway.</li><li>Drive in heavy rain at speed.</li><li>Ignore for more than 7 days.</li><li>Tap the dash and call it lucky.</li></ul></div>
  </div>
</div>
""", footer_right="05 / 07  ↗")

# SLIDE 6 — DECODE BY CODE
SLIDE6 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:24px;">
  <div class="eyebrow-section" style="color:#C73E2C;">COMMON FAULT CODES</div>
  <div class="headline" style="font-size:62px;">Read the<br/>code. <span class="accent">Save the time.</span></div>
  <table class="spec-table" style="margin-top:14px;">
    <thead><tr><th></th><th>Code</th><th>Meaning</th><th>Fix likely</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>C0035</td><td>Front-left wheel speed<br/>sensor circuit</td><td>Clean / replace<br/>sensor</td></tr>
      <tr><td>2</td><td>C0040</td><td>Front-right wheel speed<br/>sensor circuit</td><td>Clean / replace<br/>sensor</td></tr>
      <tr><td>3</td><td>C0050</td><td>Rear wheel speed sensor<br/>circuit</td><td>Wiring + sensor</td></tr>
      <tr><td>4</td><td>C0110</td><td>ABS pump motor circuit<br/>open or short</td><td>Module repair<br/>or replace</td></tr>
      <tr><td>5</td><td>C0245</td><td>Wheel speed sensor<br/>frequency error</td><td>Reluctor / sensor<br/>replacement</td></tr>
    </tbody>
  </table>
</div>
""", footer_right="06 / 07  ↗")

# SLIDE 7 — CTA
SLIDE7 = page("""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section" style="color:#C73E2C;">FREE OBD SCAN ON ABS LIGHTS</div>
  <div class="headline" style="font-size:88px;">If the ABS<br/>light is on,<br/><span class="accent">come scan.</span></div>
  <div class="divider"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:22px;">W</div>
    <div><div style="font-weight:800; font-size:22px;">WhatsApp</div><div class="body-copy">+65 9855 8423</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">📍</div>
    <div><div style="font-weight:800; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div>
  </div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;">
    <div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">↗</div>
    <div><div style="font-weight:800; font-size:22px;">therightworkshop.com</div><div class="body-copy">Link in bio</div></div>
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
