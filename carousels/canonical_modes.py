"""Canonical mode templates — exact CSS extracted from /tmp/trw-bbtb-mode-mockups/.

Each mode_X(brief) returns a list of (filename, html) tuples for slides 2..N
(slide 1 is the existing approved slide.png — handled by the runner, NOT this module).

Rules: NO page index. NO foreign coloured zones. Footer chrome sits on the
mode's natural background (paper, dark photo, cream, light grey).
"""

# Brand orange — used across ALL modes
ORANGE = "#EF5927"

# TRW logo path (relative to where rendered HTML is loaded)
LOGO_PATH = "/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/canonical/trw-logo-white.png"
def logo_uri():
    import base64
    try:
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{b64}"
    except Exception:
        return ""

LOGO_DATA_URI = logo_uri()


def to_data_uri(url):
    """If `url` is a local file:// or absolute path, convert to base64 data URI so Playwright renders it.
    Otherwise return unchanged."""
    import base64, os
    if url.startswith("file://"):
        path = url.replace("file://", "", 1)
    elif url.startswith("/"):
        path = url
    else:
        return url
    if not os.path.isfile(path):
        return url
    ext = path.lower().rsplit(".", 1)[-1]
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


# ============================================================================
# MODE B — CREAM MAGAZINE (Fraunces serif, paper bg)
# ============================================================================
MODE_B_CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Space+Grotesk:wght@500;700&family=Fraunces:wght@400;700;900&display=swap');
:root { --paper:#efe9dd; --paper-2:#e3dccc; --ink:#1a1714; --ink-soft:#3a342c; --orange:#EF5927; --rule:#1a1714; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1350px; margin:0; padding:0; background:var(--paper); font-family:'Inter',system-ui,sans-serif; color:var(--ink); overflow:hidden; }
.slide { width:1080px; height:1350px; position:relative; overflow:hidden;
  background: radial-gradient(circle at 20% 100%, rgba(0,0,0,0.05), transparent 60%), linear-gradient(180deg, var(--paper) 0%, var(--paper-2) 100%); }
.grain { position:absolute; inset:0; background-image: radial-gradient(rgba(0,0,0,0.04) 1px, transparent 1px); background-size: 4px 4px; opacity:0.5; pointer-events:none; }
.top-row { position:absolute; top:56px; left:56px; right:56px; display:flex; justify-content:space-between; align-items:center; z-index:5; }
.brand img { display:block; height:52px; width:auto; filter: invert(0.9) brightness(0.15) saturate(0); }
.series-meta { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:20px; letter-spacing:0.32em; text-transform:uppercase; color:var(--ink); }
.bottom-rule { position:absolute; bottom:120px; left:56px; right:56px; border-top:1px solid var(--rule); opacity:0.35; }
.byline { position:absolute; bottom:60px; left:56px; right:56px; display:flex; justify-content:space-between; align-items:center; }
.byline-left { font-family:'Space Grotesk',sans-serif; font-weight:500; font-size:18px; letter-spacing:0.24em; text-transform:uppercase; color:var(--ink-soft); }
.byline-right { font-family:'Fraunces',serif; font-style:italic; font-weight:700; font-size:22px; color:var(--ink); display:inline-flex; align-items:center; gap:10px; }
.byline-right .arr { color:var(--orange); font-style:normal; font-weight:900; }
"""


def _b_chrome(series_meta, byline_text="Read on"):
    return f"""
<div class="grain"></div>
<div class="top-row">
  <div class="brand"><img src="{LOGO_DATA_URI}"></div>
  <div class="series-meta">{series_meta}</div>
</div>
<div class="bottom-rule"></div>
<div class="byline">
  <div class="byline-left">Reviewed by The Right Workshop team</div>
  <div class="byline-right">{byline_text} <span class="arr">→</span></div>
</div>
"""


def b_pullquote(brief, kicker_label, h1_html, body_html):
    """Mode B layout: pull-quote — Fraunces serif headline, body below."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_B_CSS_BASE}
.kicker {{ display:flex; align-items:center; gap:16px; margin-bottom:22px; }}
.kicker .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; color:var(--ink); }}
.kicker-rule {{ flex:1; height:1px; background:var(--rule); opacity:0.45; }}
h1 {{ font-family:'Fraunces',serif; font-weight:900; font-size:120px; line-height:0.96; letter-spacing:-0.025em; color:var(--ink); margin-bottom:32px; }}
h1 em {{ font-style:normal; font-weight:900; color:var(--orange); }}
.lead {{ font-family:'Inter',sans-serif; font-weight:400; font-size:30px; line-height:1.5; color:var(--ink-soft); max-width:90%; }}
.lead strong {{ color:var(--ink); font-weight:700; }}
.article {{ position:absolute; left:56px; right:56px; top:280px; z-index:5; }}
</style></head><body>
<div class="slide">
{_b_chrome(brief['series_meta'])}
<div class="article">
  <div class="kicker"><span class="label">{kicker_label}</span><span class="kicker-rule"></span></div>
  <h1>{h1_html}</h1>
  <p class="lead">{body_html}</p>
</div>
</div></body></html>"""


def b_photo_caption(brief, kicker_label, photo_url, photo_caption_text, h1_html, body_html):
    photo_url = to_data_uri(photo_url)
    """Mode B layout: photo card with caption (slide variant of cover)."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_B_CSS_BASE}
.photo-card {{ position:absolute; top:160px; left:56px; right:56px; height:520px; border:1px solid rgba(26,23,20,0.28); background:#0e0e10; overflow:hidden; box-shadow: 0 24px 60px -28px rgba(0,0,0,0.45); }}
.photo-card .photo-img {{ position:absolute; inset:0; background-image:url('{photo_url}'); background-size:cover; background-position:center 50%; filter: saturate(1.05); }}
.photo-card::after {{ content:''; position:absolute; inset:0; background: linear-gradient(180deg, rgba(0,0,0,0.1), rgba(0,0,0,0) 30%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.55)); }}
.photo-caption {{ position:absolute; left:24px; bottom:20px; font-family:'Space Grotesk',sans-serif; font-weight:500; font-size:16px; letter-spacing:0.24em; text-transform:uppercase; color:rgba(255,255,255,0.85); z-index:2; }}
.article {{ position:absolute; left:56px; right:56px; top:720px; z-index:5; }}
.kicker {{ display:flex; align-items:center; gap:16px; margin-bottom:22px; }}
.kicker .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; }}
.kicker-rule {{ flex:1; height:1px; background:var(--rule); opacity:0.45; }}
h1 {{ font-family:'Fraunces',serif; font-weight:900; font-size:88px; line-height:0.96; letter-spacing:-0.02em; margin-bottom:24px; }}
h1 em {{ font-style:normal; color:var(--orange); }}
.lead {{ font-family:'Inter',sans-serif; font-size:24px; line-height:1.5; color:var(--ink-soft); max-width:92%; }}
.lead strong {{ color:var(--ink); font-weight:700; }}
</style></head><body>
<div class="slide">
{_b_chrome(brief['series_meta'])}
<div class="photo-card"><div class="photo-img"></div><div class="photo-caption">{photo_caption_text}</div></div>
<div class="article">
  <div class="kicker"><span class="label">{kicker_label}</span><span class="kicker-rule"></span></div>
  <h1>{h1_html}</h1>
  <p class="lead">{body_html}</p>
</div>
</div></body></html>"""


def b_numbered_list(brief, kicker_label, h1_html, items):
    """Mode B layout: numbered list (Fraunces orange numerals + Inter body)."""
    items_html = ""
    for i, it in enumerate(items, start=1):
        items_html += f"""<div style="display:grid; grid-template-columns:80px 1fr; gap:24px; align-items:flex-start; padding:24px 0; border-top:1px solid rgba(26,23,20,0.18);">
  <div style="font-family:'Fraunces',serif; font-weight:900; font-size:64px; color:var(--orange); line-height:0.9;">{i:02d}</div>
  <div>
    <div style="font-family:'Fraunces',serif; font-weight:700; font-size:38px; line-height:1.05; color:var(--ink); margin-bottom:8px;">{it['title']}</div>
    <div style="font-family:'Inter',sans-serif; font-size:21px; line-height:1.45; color:var(--ink-soft);">{it['body']}</div>
  </div>
</div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_B_CSS_BASE}
.article {{ position:absolute; left:56px; right:56px; top:160px; z-index:5; }}
.kicker {{ display:flex; align-items:center; gap:16px; margin-bottom:22px; }}
.kicker .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; }}
.kicker-rule {{ flex:1; height:1px; background:var(--rule); opacity:0.45; }}
h1 {{ font-family:'Fraunces',serif; font-weight:900; font-size:78px; line-height:0.96; letter-spacing:-0.02em; margin-bottom:36px; }}
h1 em {{ font-style:normal; color:var(--orange); }}
</style></head><body>
<div class="slide">
{_b_chrome(brief['series_meta'])}
<div class="article">
  <div class="kicker"><span class="label">{kicker_label}</span><span class="kicker-rule"></span></div>
  <h1>{h1_html}</h1>
  {items_html}
</div>
</div></body></html>"""


def b_two_column(brief, kicker_label, h1_html, left_label, left_value, left_body, right_label, right_value, right_body, footer_note=""):
    """Mode B layout: two-column comparison (no foreign dark cards — uses paper bg)."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_B_CSS_BASE}
.article {{ position:absolute; left:56px; right:56px; top:200px; z-index:5; }}
.kicker {{ display:flex; align-items:center; gap:16px; margin-bottom:22px; }}
.kicker .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; }}
.kicker-rule {{ flex:1; height:1px; background:var(--rule); opacity:0.45; }}
h1 {{ font-family:'Fraunces',serif; font-weight:900; font-size:88px; line-height:0.96; margin-bottom:48px; }}
h1 em {{ font-style:normal; color:var(--orange); }}
.cols {{ display:grid; grid-template-columns:1fr 1fr; gap:48px; border-top:1.5px solid var(--rule); padding-top:32px; }}
.col .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:14px; letter-spacing:0.3em; text-transform:uppercase; color:var(--orange); margin-bottom:14px; }}
.col .value {{ font-family:'Fraunces',serif; font-weight:900; font-size:96px; line-height:0.92; color:var(--ink); margin-bottom:16px; }}
.col .body {{ font-family:'Inter',sans-serif; font-size:22px; line-height:1.45; color:var(--ink-soft); }}
.footer-note {{ position:absolute; left:56px; right:56px; bottom:200px; font-family:'Fraunces',serif; font-style:italic; font-size:24px; color:var(--ink-soft); text-align:center; }}
</style></head><body>
<div class="slide">
{_b_chrome(brief['series_meta'])}
<div class="article">
  <div class="kicker"><span class="label">{kicker_label}</span><span class="kicker-rule"></span></div>
  <h1>{h1_html}</h1>
  <div class="cols">
    <div class="col"><div class="label">{left_label}</div><div class="value">{left_value}</div><div class="body">{left_body}</div></div>
    <div class="col"><div class="label">{right_label}</div><div class="value">{right_value}</div><div class="body">{right_body}</div></div>
  </div>
</div>
<div class="footer-note">{footer_note}</div>
</div></body></html>"""


def b_cta(brief, kicker_label, h1_html, body):
    """Mode B layout: CTA — Fraunces serif headline + contact lines on cream paper."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_B_CSS_BASE}
.article {{ position:absolute; left:56px; right:56px; top:200px; z-index:5; }}
.kicker {{ display:flex; align-items:center; gap:16px; margin-bottom:22px; }}
.kicker .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; }}
.kicker-rule {{ flex:1; height:1px; background:var(--rule); opacity:0.45; }}
h1 {{ font-family:'Fraunces',serif; font-weight:900; font-size:108px; line-height:0.94; margin-bottom:32px; }}
h1 em {{ font-style:normal; color:var(--orange); }}
.lead {{ font-family:'Inter',sans-serif; font-size:26px; line-height:1.5; color:var(--ink-soft); max-width:88%; margin-bottom:48px; }}
.contacts {{ font-family:'Inter',sans-serif; font-size:22px; line-height:1.6; color:var(--ink); }}
.contacts .row {{ display:flex; align-items:baseline; gap:16px; padding:14px 0; border-top:1px solid rgba(26,23,20,0.18); }}
.contacts .row .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:14px; letter-spacing:0.28em; text-transform:uppercase; color:var(--orange); width:160px; }}
.contacts .row .val {{ font-weight:500; }}
</style></head><body>
<div class="slide">
{_b_chrome(brief['series_meta'])}
<div class="article">
  <div class="kicker"><span class="label">{kicker_label}</span><span class="kicker-rule"></span></div>
  <h1>{h1_html}</h1>
  <p class="lead">{body}</p>
  <div class="contacts">
    <div class="row"><span class="label">WhatsApp</span><span class="val">+65 9855 8423</span></div>
    <div class="row"><span class="label">Workshop</span><span class="val">Autobay @ Kaki Bukit, #02-61</span></div>
    <div class="row"><span class="label">Web</span><span class="val">therightworkshop.com · link in bio</span></div>
  </div>
</div>
</div></body></html>"""


# ============================================================================
# MODE A — EDITORIAL DARK
# ============================================================================
MODE_A_CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Space+Grotesk:wght@500;700&family=Fraunces:wght@400;700;900&display=swap');
:root { --cream:#f5f1ea; --muted:rgba(245,241,234,0.78); --orange:#EF5927; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1350px; margin:0; padding:0; background:#07070a; font-family:'Inter',system-ui,sans-serif; color:var(--cream); overflow:hidden; }
.slide { width:1080px; height:1350px; position:relative; overflow:hidden; }
.photo { position:absolute; inset:0; background-size:cover; background-position:center 40%; filter: saturate(1.05) contrast(1.05); }
.overlay { position:absolute; inset:0; background: linear-gradient(180deg, rgba(7,7,10,0.35) 0%, rgba(7,7,10,0.42) 38%, rgba(7,7,10,0.72) 65%, rgba(7,7,10,0.92) 100%); }
.orange-glow { position:absolute; inset:0; background: radial-gradient(circle at 12% 8%, rgba(239,89,39,0.18), transparent 38%); mix-blend-mode:screen; }
.top-row { position:absolute; top:56px; left:56px; right:56px; display:flex; justify-content:space-between; align-items:center; z-index:5; }
.brand img { display:block; height:56px; width:auto; opacity:0.95; }
.series-meta { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:22px; letter-spacing:0.28em; text-transform:uppercase; color:var(--cream); }
.footer-bar { position:absolute; left:56px; right:56px; bottom:36px; z-index:5; display:flex; align-items:center; justify-content:space-between; }
.footer-bar .meta { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:17px; letter-spacing:0.24em; text-transform:uppercase; color:rgba(245,241,234,0.80); }
.footer-bar .swipe { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.3em; text-transform:uppercase; color:var(--cream); display:inline-flex; align-items:center; gap:8px; }
.footer-bar .swipe .arr { color:var(--orange); font-size:24px; }
"""


def _a_chrome(series_meta, footer_meta="HONEST BY DESIGN", footer_swipe="SWIPE"):
    return f"""
<div class="orange-glow"></div>
<div class="top-row">
  <div class="brand"><img src="{LOGO_DATA_URI}"></div>
  <div class="series-meta">{series_meta}</div>
</div>
<div class="footer-bar">
  <div class="meta">{footer_meta}</div>
  <div class="swipe">{footer_swipe} <span class="arr">→</span></div>
</div>
"""


def _a_photo_overlay(photo_url):
    return f"""<div class="photo" style="background-image:url('{photo_url}');"></div>
<div class="overlay"></div>"""


def a_pillrise(brief, photo_url, pill_text, eyebrow_text, h1_html, body_html, footer_meta="HONEST BY DESIGN"):
    photo_url = to_data_uri(photo_url)
    """Mode A layout: orange pill + headline rising over photo (variant of cover)."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_A_CSS_BASE}
.content {{ position:absolute; left:56px; right:56px; bottom:120px; z-index:5; }}
.eyebrow-strip {{ display:inline-flex; align-items:center; gap:14px; margin-bottom:28px; }}
.eyebrow-pill {{ background:var(--orange); color:#fff; font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.22em; text-transform:uppercase; padding:9px 16px; border-radius:4px; }}
.eyebrow-text {{ font-family:'Space Grotesk',sans-serif; font-weight:500; font-size:20px; letter-spacing:0.24em; text-transform:uppercase; color:var(--muted); }}
h1 {{ font-family:'Inter',sans-serif; font-weight:800; font-size:96px; line-height:0.95; letter-spacing:-0.03em; color:var(--cream); margin-bottom:26px; }}
h1 em {{ color:var(--orange); font-style:normal; font-weight:800; }}
.sub {{ font-family:'Inter',sans-serif; font-weight:400; font-size:26px; line-height:1.45; color:var(--muted); max-width:90%; }}
.sub strong {{ color:var(--cream); font-weight:700; }}
</style></head><body>
<div class="slide">
{_a_photo_overlay(photo_url)}
{_a_chrome(brief['series_meta'], footer_meta)}
<div class="content">
  <div class="eyebrow-strip"><span class="eyebrow-pill">{pill_text}</span><span class="eyebrow-text">{eyebrow_text}</span></div>
  <h1>{h1_html}</h1>
  <p class="sub">{body_html}</p>
</div>
</div></body></html>"""


def a_numbered_card(brief, photo_url, num, label, h1_html, body_html, watch_text="", footer_meta="HONEST BY DESIGN"):
    photo_url = to_data_uri(photo_url)
    """Mode A layout: big orange-pill number + headline + body + 'watch for' line over photo."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_A_CSS_BASE}
.content {{ position:absolute; left:56px; right:56px; bottom:140px; z-index:5; }}
.num-row {{ display:flex; align-items:center; gap:20px; margin-bottom:24px; }}
.num-pill {{ background:var(--orange); color:#fff; font-family:'Inter',sans-serif; font-weight:900; font-size:58px; letter-spacing:-0.02em; padding:6px 22px; border-radius:6px; line-height:1; }}
.num-label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; color:var(--muted); }}
h1 {{ font-family:'Inter',sans-serif; font-weight:800; font-size:84px; line-height:0.95; letter-spacing:-0.03em; color:var(--cream); margin-bottom:24px; }}
h1 em {{ color:var(--orange); font-style:normal; font-weight:800; }}
.sub {{ font-family:'Inter',sans-serif; font-weight:400; font-size:24px; line-height:1.45; color:var(--muted); max-width:88%; margin-bottom:24px; }}
.sub strong {{ color:var(--cream); font-weight:700; }}
.watch {{ font-family:'Fraunces',serif; font-style:italic; font-weight:400; font-size:22px; color:rgba(245,241,234,0.75); border-top:1px solid rgba(245,241,234,0.22); padding-top:16px; max-width:88%; }}
</style></head><body>
<div class="slide">
{_a_photo_overlay(photo_url)}
{_a_chrome(brief['series_meta'], footer_meta)}
<div class="content">
  <div class="num-row"><span class="num-pill">{num:02d}</span><span class="num-label">{label}</span></div>
  <h1>{h1_html}</h1>
  <p class="sub">{body_html}</p>
  {'<div class="watch">'+watch_text+'</div>' if watch_text else ''}
</div>
</div></body></html>"""


def a_quote(brief, photo_url, kicker, quote_html, attrib, footer_meta="HONEST BY DESIGN"):
    photo_url = to_data_uri(photo_url)
    """Mode A layout: pull quote in Fraunces serif italic over photo."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_A_CSS_BASE}
.content {{ position:absolute; left:56px; right:56px; bottom:160px; z-index:5; }}
.kicker {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; color:var(--orange); margin-bottom:30px; }}
.quote {{ font-family:'Fraunces',serif; font-weight:400; font-style:italic; font-size:78px; line-height:1.05; letter-spacing:-0.015em; color:var(--cream); margin-bottom:36px; }}
.quote em {{ color:var(--orange); font-style:italic; font-weight:700; }}
.attrib {{ font-family:'Space Grotesk',sans-serif; font-weight:500; font-size:18px; letter-spacing:0.24em; text-transform:uppercase; color:var(--muted); }}
</style></head><body>
<div class="slide">
{_a_photo_overlay(photo_url)}
{_a_chrome(brief['series_meta'], footer_meta)}
<div class="content">
  <div class="kicker">{kicker}</div>
  <div class="quote">"{quote_html}"</div>
  <div class="attrib">— {attrib}</div>
</div>
</div></body></html>"""


def a_cta(brief, photo_url, h1_html, body_html, footer_meta="HONEST BY DESIGN"):
    photo_url = to_data_uri(photo_url)
    """Mode A CTA: Inter headline over photo + contact rows."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_A_CSS_BASE}
.content {{ position:absolute; left:56px; right:56px; bottom:120px; z-index:5; }}
h1 {{ font-family:'Inter',sans-serif; font-weight:800; font-size:96px; line-height:0.95; letter-spacing:-0.03em; color:var(--cream); margin-bottom:30px; }}
h1 em {{ color:var(--orange); font-style:normal; font-weight:800; }}
.lead {{ font-family:'Inter',sans-serif; font-weight:400; font-size:24px; line-height:1.5; color:var(--muted); max-width:88%; margin-bottom:36px; }}
.contacts {{ border-top:1px solid rgba(245,241,234,0.22); padding-top:20px; }}
.contacts .row {{ display:flex; align-items:baseline; gap:18px; padding:10px 0; }}
.contacts .row .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:13px; letter-spacing:0.28em; text-transform:uppercase; color:var(--orange); width:130px; }}
.contacts .row .val {{ font-family:'Inter',sans-serif; font-size:22px; color:var(--cream); }}
</style></head><body>
<div class="slide">
{_a_photo_overlay(photo_url)}
{_a_chrome(brief['series_meta'], footer_meta)}
<div class="content">
  <h1>{h1_html}</h1>
  <p class="lead">{body_html}</p>
  <div class="contacts">
    <div class="row"><span class="label">WhatsApp</span><span class="val">+65 9855 8423</span></div>
    <div class="row"><span class="label">Workshop</span><span class="val">Autobay @ Kaki Bukit, #02-61</span></div>
    <div class="row"><span class="label">Web</span><span class="val">therightworkshop.com · link in bio</span></div>
  </div>
</div>
</div></body></html>"""


# ============================================================================
# MODE C — POSTER BOLD
# ============================================================================
MODE_C_CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Space+Grotesk:wght@500;700&family=Bebas+Neue&display=swap');
:root { --cream:#f5f1ea; --ink:#0a0a0c; --orange:#EF5927; --muted:rgba(245,241,234,0.78); }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1350px; margin:0; padding:0; background:var(--ink); font-family:'Inter',system-ui,sans-serif; color:var(--cream); overflow:hidden; }
.slide { width:1080px; height:1350px; position:relative; overflow:hidden; }
.photo-zone { position:absolute; top:0; left:0; right:0; height:780px; overflow:hidden; }
.photo-zone .photo { position:absolute; inset:0; background-size:cover; background-position:center 45%; filter: contrast(1.05) saturate(1.05); }
.photo-zone .grain { position:absolute; inset:0; background-image:radial-gradient(rgba(0,0,0,0.06) 1px, transparent 1px); background-size:3px 3px; opacity:0.5; mix-blend-mode:multiply; }
.photo-zone::after { content:''; position:absolute; left:0; right:0; bottom:0; height:200px; background:linear-gradient(180deg, transparent 0%, rgba(10,10,12,0.7) 70%, var(--ink) 100%); }
.cut { position:absolute; top:740px; left:0; right:0; height:80px; background:var(--ink); clip-path: polygon(0 35%, 100% 0%, 100% 100%, 0 100%); }
.top-row { position:absolute; top:48px; left:56px; right:56px; display:flex; justify-content:space-between; align-items:center; z-index:5; }
.brand img { display:block; height:52px; width:auto; opacity:0.95; }
.top-meta { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.32em; text-transform:uppercase; color:var(--cream); background:var(--orange); padding:9px 16px; border-radius:2px; }
.bottom-strip { position:absolute; bottom:36px; left:56px; right:56px; display:flex; align-items:center; justify-content:space-between; z-index:5; }
.bottom-strip .stat { font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:34px; letter-spacing:0.06em; color:var(--cream); }
.bottom-strip .stat .num { font-size:46px; vertical-align:-2px; margin-right:10px; color:var(--orange); }
.bottom-strip .swipe { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:20px; letter-spacing:0.3em; text-transform:uppercase; color:var(--cream); display:inline-flex; align-items:center; gap:10px; }
.bottom-strip .swipe .arr { color:var(--orange); font-size:26px; }
"""


def _c_chrome(series_meta, footer_stat_html="<span class='num'>'26</span>RECALL DECODED"):
    return f"""
<div class="top-row"><div class="brand"><img src="{LOGO_DATA_URI}"></div><div class="top-meta">{series_meta}</div></div>
<div class="bottom-strip"><div class="stat">{footer_stat_html}</div><div class="swipe">SWIPE <span class="arr">&rarr;</span></div></div>
"""


def c_photo_headline(brief, photo_url, badge_year_html, badge_tag, h1_html, tagline_html, footer_stat=""):
    photo_url = to_data_uri(photo_url)
    """Mode C layout: top-half photo, diagonal cut, badge strip, Bebas Neue HUGE headline."""
    fs = footer_stat or "<span class='num'>'26</span>DECODED"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_C_CSS_BASE}
.badge-strip {{ position:absolute; top:660px; left:56px; right:56px; z-index:6; display:flex; align-items:center; gap:18px; }}
.badge-year {{ font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:64px; line-height:1; color:var(--orange); letter-spacing:0.04em; }}
.badge-rule {{ flex:1; height:2px; background:var(--cream); opacity:0.6; }}
.badge-tag {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.32em; text-transform:uppercase; color:var(--cream); }}
.poster-headline {{ position:absolute; left:56px; right:56px; top:790px; z-index:5; }}
h1 {{ font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:130px; line-height:0.86; letter-spacing:0.005em; color:var(--cream); text-transform:uppercase; }}
h1 .accent {{ color:var(--orange); }}
.tagline {{ font-family:'Inter',sans-serif; font-weight:500; font-size:22px; line-height:1.4; color:var(--muted); margin-top:18px; max-width:90%; }}
.tagline strong {{ color:var(--cream); font-weight:800; }}
</style></head><body>
<div class="slide">
<div class="photo-zone"><div class="photo" style="background-image:url('{photo_url}');"></div><div class="grain"></div></div>
<div class="cut"></div>
{_c_chrome(brief['series_meta'], fs)}
<div class="badge-strip"><div class="badge-year">{badge_year_html}</div><div class="badge-rule"></div><div class="badge-tag">{badge_tag}</div></div>
<div class="poster-headline"><h1>{h1_html}</h1><p class="tagline">{tagline_html}</p></div>
</div></body></html>"""


def c_stat_callout(brief, big_stat_html, eyebrow, h1_html, body_html, footer_stat=""):
    """Mode C layout: dark full-bg, big Bebas Neue stat callout, Inter body."""
    fs = footer_stat or "<span class='num'>'26</span>DECODED"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_C_CSS_BASE}
.body-bg {{ position:absolute; inset:0; background: radial-gradient(circle at 90% 20%, rgba(239,89,39,0.10), transparent 50%), var(--ink); }}
.content {{ position:absolute; top:200px; left:56px; right:56px; }}
.eyebrow {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.32em; text-transform:uppercase; color:var(--orange); margin-bottom:32px; }}
.big {{ font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:240px; line-height:0.9; letter-spacing:0.02em; color:var(--cream); margin-bottom:14px; }}
.big .accent {{ color:var(--orange); }}
h1 {{ font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:96px; line-height:0.92; letter-spacing:0.01em; color:var(--cream); text-transform:uppercase; margin-bottom:32px; }}
h1 .accent {{ color:var(--orange); }}
.body {{ font-family:'Inter',sans-serif; font-weight:500; font-size:24px; line-height:1.5; color:var(--muted); max-width:88%; }}
.body strong {{ color:var(--cream); font-weight:800; }}
</style></head><body>
<div class="slide">
<div class="body-bg"></div>
{_c_chrome(brief['series_meta'], fs)}
<div class="content">
  <div class="eyebrow">{eyebrow}</div>
  <div class="big">{big_stat_html}</div>
  <h1>{h1_html}</h1>
  <p class="body">{body_html}</p>
</div>
</div></body></html>"""


def c_list_punch(brief, eyebrow, h1_html, items, footer_stat=""):
    """Mode C layout: dark full-bg, list of punchy items in Bebas Neue."""
    fs = footer_stat or "<span class='num'>'26</span>DECODED"
    items_html = ""
    for i, it in enumerate(items, start=1):
        items_html += f"""<div style="display:grid; grid-template-columns:90px 1fr; gap:24px; align-items:flex-start; padding:24px 0; border-top:1px solid rgba(245,241,234,0.18);">
  <div style="font-family:'Bebas Neue',sans-serif; font-size:74px; line-height:0.9; color:var(--orange); letter-spacing:0.04em;">{i:02d}</div>
  <div>
    <div style="font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:54px; line-height:0.95; letter-spacing:0.02em; color:var(--cream); text-transform:uppercase; margin-bottom:8px;">{it['title']}</div>
    <div style="font-family:'Inter',sans-serif; font-size:22px; line-height:1.45; color:var(--muted);">{it['body']}</div>
  </div>
</div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_C_CSS_BASE}
.body-bg {{ position:absolute; inset:0; background:var(--ink); }}
.content {{ position:absolute; top:160px; left:56px; right:56px; }}
.eyebrow {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:18px; letter-spacing:0.32em; text-transform:uppercase; color:var(--orange); margin-bottom:24px; }}
h1 {{ font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:96px; line-height:0.92; letter-spacing:0.01em; color:var(--cream); text-transform:uppercase; margin-bottom:24px; }}
h1 .accent {{ color:var(--orange); }}
</style></head><body>
<div class="slide">
<div class="body-bg"></div>
{_c_chrome(brief['series_meta'], fs)}
<div class="content">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{h1_html}</h1>
  {items_html}
</div>
</div></body></html>"""


def c_cta(brief, h1_html, body_html, footer_stat=""):
    """Mode C CTA: Bebas Neue headline + contacts on dark."""
    fs = footer_stat or "BOOK NOW"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_C_CSS_BASE}
.body-bg {{ position:absolute; inset:0; background: radial-gradient(circle at 50% 30%, rgba(239,89,39,0.18), transparent 55%), var(--ink); }}
.content {{ position:absolute; top:230px; left:56px; right:56px; }}
h1 {{ font-family:'Bebas Neue',sans-serif; font-weight:400; font-size:140px; line-height:0.86; letter-spacing:0.01em; color:var(--cream); text-transform:uppercase; margin-bottom:28px; }}
h1 .accent {{ color:var(--orange); }}
.body {{ font-family:'Inter',sans-serif; font-size:26px; line-height:1.45; color:var(--muted); max-width:88%; margin-bottom:40px; }}
.body strong {{ color:var(--cream); font-weight:800; }}
.contacts {{ border-top:1px solid rgba(245,241,234,0.22); padding-top:24px; }}
.contacts .row {{ display:flex; align-items:baseline; gap:18px; padding:10px 0; }}
.contacts .row .label {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:13px; letter-spacing:0.28em; text-transform:uppercase; color:var(--orange); width:130px; }}
.contacts .row .val {{ font-family:'Inter',sans-serif; font-size:22px; color:var(--cream); }}
</style></head><body>
<div class="slide">
<div class="body-bg"></div>
{_c_chrome(brief['series_meta'], fs)}
<div class="content">
  <h1>{h1_html}</h1>
  <p class="body">{body_html}</p>
  <div class="contacts">
    <div class="row"><span class="label">WhatsApp</span><span class="val">+65 9855 8423</span></div>
    <div class="row"><span class="label">Workshop</span><span class="val">Autobay @ Kaki Bukit, #02-61</span></div>
    <div class="row"><span class="label">Web</span><span class="val">therightworkshop.com · link in bio</span></div>
  </div>
</div>
</div></body></html>"""


# ============================================================================
# MODE D — POLAROID ZINE
# ============================================================================
MODE_D_CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&family=Space+Grotesk:wght@500;700&family=Caveat:wght@400;700&family=Special+Elite&display=swap');
:root { --paper:#e8e0d2; --paper-2:#d8cfbe; --ink:#171410; --ink-soft:#3a342a; --orange:#EF5927; --tape:#f8e896; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1350px; margin:0; padding:0; background:var(--paper); font-family:'Inter',system-ui,sans-serif; color:var(--ink); overflow:hidden; }
.slide { width:1080px; height:1350px; position:relative; overflow:hidden; background: radial-gradient(circle at 8% 8%, rgba(0,0,0,0.04), transparent 35%), radial-gradient(circle at 92% 88%, rgba(0,0,0,0.06), transparent 40%), linear-gradient(170deg, var(--paper), var(--paper-2)); }
.grain { position:absolute; inset:0; background-image: radial-gradient(rgba(0,0,0,0.06) 1px, transparent 1px), radial-gradient(rgba(255,255,255,0.04) 1px, transparent 1px); background-size: 4px 4px, 7px 7px; background-position: 0 0, 2px 2px; opacity:0.6; mix-blend-mode:multiply; pointer-events:none; }
.top-row { position:absolute; top:48px; left:56px; right:56px; display:flex; justify-content:space-between; align-items:center; z-index:5; }
.brand img { display:block; height:48px; width:auto; filter: invert(0.9) brightness(0.18) saturate(0); }
.series-meta { font-family:'Special Elite',monospace; font-weight:400; font-size:18px; letter-spacing:0.18em; text-transform:uppercase; color:var(--ink); }
.corner-stamp { position:absolute; bottom:50px; left:56px; font-family:'Special Elite',monospace; font-weight:400; font-size:13px; letter-spacing:0.22em; text-transform:uppercase; color:var(--ink); z-index:5; border:1.5px solid var(--ink); padding:8px 12px; transform:rotate(-1deg); }
.scribble-swipe { position:absolute; bottom:48px; right:56px; font-family:'Caveat',cursive; font-weight:700; font-size:38px; color:var(--orange); display:inline-flex; align-items:center; gap:10px; z-index:5; transform:rotate(-2deg); }
.scribble-swipe .arr { font-size:48px; }
"""


def _d_chrome(series_meta, swipe="read it"):
    return f"""
<div class="grain"></div>
<div class="top-row"><div class="brand"><img src="{LOGO_DATA_URI}"></div><div class="series-meta">{series_meta}</div></div>
<div class="corner-stamp">The Right Workshop · KB SG</div>
<div class="scribble-swipe">{swipe} <span class="arr">→</span></div>
"""


def d_polaroid_text(brief, photo_url, photo_caption, sticky_lines, kicker_stamp, kicker_date, h1_html, lead_text, swipe="read it"):
    photo_url = to_data_uri(photo_url)
    """Mode D layout: tilted polaroid + sticky note + Caveat headline + Special Elite body."""
    sticky_html = "<br>".join(sticky_lines)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_D_CSS_BASE}
.polaroid {{ position:absolute; top:160px; left:130px; width:660px; height:660px; background:#fafaf6; padding:24px 24px 90px; border:1px solid rgba(0,0,0,0.08); box-shadow: 0 4px 0 rgba(0,0,0,0.05), 0 22px 48px -18px rgba(0,0,0,0.45); transform: rotate(-3deg); z-index:3; }}
.polaroid .photo-img {{ width:100%; height:546px; background-image:url('{photo_url}'); background-size:cover; background-position:center; background-color:#222; }}
.polaroid .photo-cap {{ margin-top:16px; text-align:center; font-family:'Caveat',cursive; font-weight:700; font-size:30px; color:#3a342a; }}
.tape {{ position:absolute; top:8px; left:50%; transform:translateX(-50%) rotate(-2deg); width:140px; height:30px; background:var(--tape); opacity:0.78; box-shadow: 0 1px 2px rgba(0,0,0,0.18); z-index:1; }}
.sticky {{ position:absolute; top:520px; right:80px; width:280px; min-height:200px; background:#fffae3; padding:24px 20px; transform:rotate(4deg); box-shadow: 0 12px 30px -12px rgba(0,0,0,0.35); font-family:'Caveat',cursive; font-weight:700; font-size:30px; line-height:1.2; color:#3a342a; z-index:4; }}
.headline-block {{ position:absolute; left:56px; right:56px; top:880px; z-index:5; }}
.kicker {{ display:flex; align-items:center; gap:12px; margin-bottom:18px; }}
.kicker .stamp {{ font-family:'Special Elite',monospace; font-weight:400; font-size:14px; letter-spacing:0.22em; text-transform:uppercase; color:#fff; background:var(--orange); padding:4px 10px; transform:rotate(-1.5deg); }}
.kicker .date {{ font-family:'Caveat',cursive; font-weight:700; font-size:28px; color:var(--ink-soft); }}
h1 {{ font-family:'Caveat',cursive; font-weight:700; font-size:106px; line-height:0.98; letter-spacing:-0.005em; color:var(--ink); margin-bottom:14px; }}
h1 .underline {{ display:inline-block; position:relative; color:var(--orange); }}
h1 .underline::after {{ content:''; position:absolute; left:-4px; right:-4px; bottom:8px; height:14px; background:rgba(239,89,39,0.22); z-index:-1; transform:rotate(-0.6deg); }}
.lead {{ font-family:'Special Elite',monospace; font-weight:400; font-size:22px; line-height:1.5; color:var(--ink); max-width:88%; margin-bottom:30px; }}
</style></head><body>
<div class="slide">
{_d_chrome(brief['series_meta'], swipe)}
<div class="polaroid"><div class="tape"></div><div class="photo-img"></div><div class="photo-cap">{photo_caption}</div></div>
<div class="sticky">{sticky_html}</div>
<div class="headline-block">
  <div class="kicker"><span class="stamp">{kicker_stamp}</span><span class="date">{kicker_date}</span></div>
  <h1>{h1_html}</h1>
  <p class="lead">{lead_text}</p>
</div>
</div></body></html>"""


def d_handwritten_list(brief, kicker_stamp, h1_html, items, swipe="read it"):
    """Mode D layout: handwritten Caveat list with Special Elite numbered bullets."""
    items_html = ""
    for i, it in enumerate(items, start=1):
        items_html += f"""<div style="display:grid; grid-template-columns:60px 1fr; gap:18px; align-items:flex-start; padding:20px 0; border-top:1px dashed rgba(23,20,16,0.4);">
  <div style="font-family:'Caveat',cursive; font-weight:700; font-size:48px; color:var(--orange); line-height:0.9;">{i}.</div>
  <div>
    <div style="font-family:'Caveat',cursive; font-weight:700; font-size:42px; line-height:1.05; color:var(--ink); margin-bottom:6px;">{it['title']}</div>
    <div style="font-family:'Special Elite',monospace; font-size:18px; line-height:1.5; color:var(--ink-soft);">{it['body']}</div>
  </div>
</div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_D_CSS_BASE}
.headline-block {{ position:absolute; left:56px; right:56px; top:160px; z-index:5; }}
.kicker {{ margin-bottom:22px; }}
.kicker .stamp {{ font-family:'Special Elite',monospace; font-weight:400; font-size:14px; letter-spacing:0.22em; text-transform:uppercase; color:#fff; background:var(--orange); padding:4px 10px; transform:rotate(-1.5deg); display:inline-block; }}
h1 {{ font-family:'Caveat',cursive; font-weight:700; font-size:96px; line-height:0.98; color:var(--ink); margin-bottom:32px; }}
h1 .underline {{ display:inline-block; position:relative; color:var(--orange); }}
h1 .underline::after {{ content:''; position:absolute; left:-4px; right:-4px; bottom:8px; height:14px; background:rgba(239,89,39,0.22); z-index:-1; }}
</style></head><body>
<div class="slide">
{_d_chrome(brief['series_meta'], swipe)}
<div class="headline-block">
  <div class="kicker"><span class="stamp">{kicker_stamp}</span></div>
  <h1>{h1_html}</h1>
  {items_html}
</div>
</div></body></html>"""


def d_sticky_quote(brief, kicker_stamp, sticky_html, attrib, swipe="read it"):
    """Mode D layout: a single big sticky-note pull quote."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_D_CSS_BASE}
.headline-block {{ position:absolute; left:56px; right:56px; top:200px; z-index:5; }}
.kicker {{ margin-bottom:34px; }}
.kicker .stamp {{ font-family:'Special Elite',monospace; font-weight:400; font-size:14px; letter-spacing:0.22em; text-transform:uppercase; color:#fff; background:var(--orange); padding:4px 10px; transform:rotate(-1.5deg); display:inline-block; }}
.big-sticky {{ background:#fffae3; padding:54px 48px; transform:rotate(-2deg); box-shadow: 0 18px 40px -16px rgba(0,0,0,0.35); font-family:'Caveat',cursive; font-weight:700; font-size:80px; line-height:1.1; color:var(--ink); margin-bottom:36px; }}
.big-sticky em {{ color:var(--orange); font-style:normal; }}
.attrib {{ font-family:'Special Elite',monospace; font-size:18px; letter-spacing:0.16em; color:var(--ink-soft); padding-left:8px; }}
</style></head><body>
<div class="slide">
{_d_chrome(brief['series_meta'], swipe)}
<div class="headline-block">
  <div class="kicker"><span class="stamp">{kicker_stamp}</span></div>
  <div class="big-sticky">{sticky_html}</div>
  <p class="attrib">— {attrib}</p>
</div>
</div></body></html>"""


def d_cta(brief, kicker_stamp, h1_html, body_html, swipe="book"):
    """Mode D CTA: Caveat headline + handwritten contact list on cream paper."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_D_CSS_BASE}
.headline-block {{ position:absolute; left:56px; right:56px; top:200px; z-index:5; }}
.kicker {{ margin-bottom:24px; }}
.kicker .stamp {{ font-family:'Special Elite',monospace; font-weight:400; font-size:14px; letter-spacing:0.22em; text-transform:uppercase; color:#fff; background:var(--orange); padding:4px 10px; transform:rotate(-1.5deg); display:inline-block; }}
h1 {{ font-family:'Caveat',cursive; font-weight:700; font-size:120px; line-height:0.96; color:var(--ink); margin-bottom:28px; }}
h1 .underline {{ display:inline-block; position:relative; color:var(--orange); }}
h1 .underline::after {{ content:''; position:absolute; left:-4px; right:-4px; bottom:8px; height:14px; background:rgba(239,89,39,0.22); z-index:-1; }}
.lead {{ font-family:'Special Elite',monospace; font-size:20px; line-height:1.5; color:var(--ink-soft); max-width:88%; margin-bottom:36px; }}
.contacts {{ font-family:'Special Elite',monospace; }}
.contacts .row {{ display:flex; align-items:baseline; gap:18px; padding:14px 0; border-top:1px dashed rgba(23,20,16,0.4); font-size:20px; }}
.contacts .row .label {{ font-weight:400; letter-spacing:0.22em; text-transform:uppercase; color:var(--orange); width:140px; }}
</style></head><body>
<div class="slide">
{_d_chrome(brief['series_meta'], swipe)}
<div class="headline-block">
  <div class="kicker"><span class="stamp">{kicker_stamp}</span></div>
  <h1>{h1_html}</h1>
  <p class="lead">{body_html}</p>
  <div class="contacts">
    <div class="row"><span class="label">WhatsApp</span><span>+65 9855 8423</span></div>
    <div class="row"><span class="label">Workshop</span><span>Autobay @ Kaki Bukit, #02-61</span></div>
    <div class="row"><span class="label">Web</span><span>therightworkshop.com · link in bio</span></div>
  </div>
</div>
</div></body></html>"""


# ============================================================================
# MODE E — SPEC SHEET
# ============================================================================
MODE_E_CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700;800;900&display=swap');
:root { --bg:#f4f3ef; --bg-2:#e9e7e0; --ink:#0c0c0e; --ink-soft:#5a5a5e; --rule:#0c0c0e; --orange:#EF5927; --grid:rgba(12,12,14,0.06); }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1350px; margin:0; padding:0; background:var(--bg); font-family:'Inter',system-ui,sans-serif; color:var(--ink); overflow:hidden; }
.slide { width:1080px; height:1350px; position:relative; overflow:hidden; background: linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%); }
.grid-bg { position:absolute; inset:0; background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px); background-size: 60px 60px; pointer-events:none; }
.top-row { position:absolute; top:48px; left:56px; right:56px; display:flex; justify-content:space-between; align-items:center; z-index:5; }
.brand img { display:block; height:50px; width:auto; filter: invert(0.92) brightness(0.12) saturate(0); }
.series-meta { font-family:'JetBrains Mono',monospace; font-weight:500; font-size:14px; letter-spacing:0.22em; text-transform:uppercase; color:var(--ink); border:1.5px solid var(--ink); padding:6px 12px; }
.footer-bar { position:absolute; left:56px; right:56px; bottom:36px; z-index:5; display:flex; align-items:center; justify-content:space-between; }
.footer-bar .meta { font-family:'JetBrains Mono',monospace; font-weight:700; font-size:18px; letter-spacing:0.26em; text-transform:uppercase; color:var(--ink); }
.footer-bar .meta b { color:var(--orange); }
.footer-bar .swipe { font-family:'JetBrains Mono',monospace; font-weight:700; font-size:18px; letter-spacing:0.28em; text-transform:uppercase; color:var(--ink); display:inline-flex; align-items:center; gap:8px; border:1.5px solid var(--ink); padding:9px 14px; }
.footer-bar .swipe .arr { color:var(--orange); font-size:22px; }
"""


def _e_chrome(series_meta, footer_meta_html="<b>BY THE NUMBERS</b>", footer_swipe="FULL SHEET"):
    return f"""
<div class="grid-bg"></div>
<div class="top-row"><div class="brand"><img src="{LOGO_DATA_URI}"></div><div class="series-meta">{series_meta}</div></div>
<div class="footer-bar"><div class="meta">{footer_meta_html}</div><div class="swipe">{footer_swipe} <span class="arr">→</span></div></div>
"""


def e_spec_table(brief, file_id, file_label, eyebrow, h1_html, body_html, cells):
    """Mode E layout: spec sheet with file header + headline + 4-column data table."""
    cells_html = ""
    for c in cells:
        cells_html += f"""<div class="spec-cell">
  <div class="k">{c['k']}</div>
  <div class="v">{c['v']}</div>
  <div class="u">{c['u']}</div>
</div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_E_CSS_BASE}
.spec-header {{ position:absolute; top:130px; left:56px; right:56px; z-index:4; display:flex; align-items:flex-end; justify-content:space-between; border-bottom:1.5px solid var(--ink); padding-bottom:14px; }}
.spec-header .left .num {{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:12px; letter-spacing:0.3em; color:var(--orange); margin-bottom:6px; }}
.spec-header .left .label {{ font-family:'Inter',sans-serif; font-weight:800; font-size:32px; line-height:1; letter-spacing:-0.01em; }}
.headline-block {{ position:absolute; top:280px; left:56px; right:56px; z-index:5; }}
.eyebrow {{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:13px; letter-spacing:0.32em; text-transform:uppercase; color:var(--orange); margin-bottom:14px; }}
h1 {{ font-family:'Inter',sans-serif; font-weight:800; font-size:88px; line-height:0.92; letter-spacing:-0.03em; color:var(--ink); margin-bottom:18px; }}
h1 .accent {{ color:var(--orange); }}
.lead {{ font-family:'Inter',sans-serif; font-weight:400; font-size:22px; line-height:1.5; color:var(--ink-soft); max-width:80%; }}
.lead strong {{ color:var(--ink); font-weight:700; }}
.spec-table {{ position:absolute; left:56px; right:56px; bottom:120px; z-index:5; display:grid; grid-template-columns:repeat(4, 1fr); border-top:1.5px solid var(--ink); border-bottom:1.5px solid var(--ink); }}
.spec-cell {{ padding:18px 14px; border-right:1px solid rgba(12,12,14,0.18); }}
.spec-cell:last-child {{ border-right:none; }}
.spec-cell .k {{ font-family:'JetBrains Mono',monospace; font-weight:500; font-size:11px; letter-spacing:0.22em; text-transform:uppercase; color:var(--ink-soft); margin-bottom:8px; }}
.spec-cell .v {{ font-family:'Inter',sans-serif; font-weight:800; font-size:32px; line-height:1; letter-spacing:-0.02em; color:var(--ink); }}
.spec-cell .u {{ font-family:'JetBrains Mono',monospace; font-weight:500; font-size:12px; color:var(--ink-soft); margin-top:4px; }}
</style></head><body>
<div class="slide">
{_e_chrome(brief['series_meta'])}
<div class="spec-header">
  <div class="left"><div class="num">{file_id}</div><div class="label">{file_label}</div></div>
</div>
<div class="headline-block">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{h1_html}</h1>
  <p class="lead">{body_html}</p>
</div>
<div class="spec-table">{cells_html}</div>
</div></body></html>"""


def e_pinned_photo(brief, photo_url, pins, eyebrow, h1_html, body_html):
    photo_url = to_data_uri(photo_url)
    """Mode E layout: photo with technical pin callouts (A/B/C/D)."""
    pins_html = ""
    for p in pins:
        pins_html += f"""<div class="pin" style="{p['pos']}">{p['label']}</div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_E_CSS_BASE}
.photo-frame {{ position:absolute; top:160px; left:56px; right:56px; height:480px; overflow:hidden; background:#0c0c0e; z-index:3; }}
.photo-frame .photo-img {{ position:absolute; inset:0; background-image:url('{photo_url}'); background-size:cover; background-position:center center; background-repeat:no-repeat; }}
.pin {{ position:absolute; z-index:4; font-family:'JetBrains Mono',monospace; font-weight:700; font-size:14px; letter-spacing:0.18em; text-transform:uppercase; color:#0c0c0e; background:rgba(255,255,255,0.96); padding:9px 16px 9px 30px; border-radius:999px; box-shadow:0 4px 14px rgba(0,0,0,0.22); display:inline-flex; align-items:center; white-space:nowrap; }}
.pin::before {{ content:''; position:absolute; left:11px; top:50%; transform:translateY(-50%); width:10px; height:10px; border-radius:50%; background:var(--orange); box-shadow:0 0 0 3px rgba(239,89,39,0.22); }}
.headline-block {{ position:absolute; top:680px; left:56px; right:56px; z-index:5; }}
.eyebrow {{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:13px; letter-spacing:0.32em; text-transform:uppercase; color:var(--orange); margin-bottom:14px; }}
h1 {{ font-family:'Inter',sans-serif; font-weight:800; font-size:96px; line-height:0.92; letter-spacing:-0.035em; color:var(--ink); margin-bottom:18px; }}
h1 .accent {{ color:var(--orange); }}
.lead {{ font-family:'Inter',sans-serif; font-weight:400; font-size:24px; line-height:1.5; color:var(--ink-soft); max-width:85%; }}
.lead strong {{ color:var(--ink); font-weight:700; }}
</style></head><body>
<div class="slide">
{_e_chrome(brief['series_meta'])}
<div class="photo-frame"><div class="photo-img"></div></div>
{pins_html}
<div class="headline-block">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{h1_html}</h1>
  <p class="lead">{body_html}</p>
</div>
</div></body></html>"""


def e_data_grid(brief, eyebrow, h1_html, items):
    """Mode E layout: 4-tile data grid (no foreign dark cards — uses light bg with rules)."""
    items_html = ""
    for it in items:
        items_html += f"""<div class="tile">
  <div class="k">{it['k']}</div>
  <div class="v">{it['v']}</div>
  <div class="u">{it['u']}</div>
</div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_E_CSS_BASE}
.headline-block {{ position:absolute; top:160px; left:56px; right:56px; z-index:5; }}
.eyebrow {{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:13px; letter-spacing:0.32em; text-transform:uppercase; color:var(--orange); margin-bottom:14px; }}
h1 {{ font-family:'Inter',sans-serif; font-weight:800; font-size:84px; line-height:0.92; letter-spacing:-0.03em; color:var(--ink); margin-bottom:50px; }}
h1 .accent {{ color:var(--orange); }}
.grid {{ position:absolute; top:520px; left:56px; right:56px; z-index:5; display:grid; grid-template-columns:1fr 1fr; gap:0; border-top:1.5px solid var(--ink); border-bottom:1.5px solid var(--ink); }}
.tile {{ padding:32px 24px; border-right:1px solid rgba(12,12,14,0.18); border-bottom:1px solid rgba(12,12,14,0.18); }}
.tile:nth-child(2n) {{ border-right:none; }}
.tile:nth-child(n+3) {{ }}
.tile:nth-last-child(-n+2) {{ border-bottom:none; }}
.tile .k {{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:13px; letter-spacing:0.28em; text-transform:uppercase; color:var(--orange); margin-bottom:12px; }}
.tile .v {{ font-family:'Inter',sans-serif; font-weight:800; font-size:64px; line-height:0.95; letter-spacing:-0.02em; color:var(--ink); margin-bottom:12px; }}
.tile .u {{ font-family:'Inter',sans-serif; font-size:18px; line-height:1.4; color:var(--ink-soft); }}
</style></head><body>
<div class="slide">
{_e_chrome(brief['series_meta'])}
<div class="headline-block">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{h1_html}</h1>
</div>
<div class="grid">{items_html}</div>
</div></body></html>"""


def e_cta(brief, h1_html, body_html):
    """Mode E CTA: Inter 800 headline + bordered contact rows on light bg."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_E_CSS_BASE}
.content {{ position:absolute; top:200px; left:56px; right:56px; z-index:5; }}
h1 {{ font-family:'Inter',sans-serif; font-weight:800; font-size:108px; line-height:0.92; letter-spacing:-0.035em; color:var(--ink); margin-bottom:32px; }}
h1 .accent {{ color:var(--orange); }}
.body {{ font-family:'Inter',sans-serif; font-size:24px; line-height:1.45; color:var(--ink-soft); max-width:88%; margin-bottom:48px; }}
.body strong {{ color:var(--ink); font-weight:700; }}
.contacts {{ border:1.5px solid var(--ink); padding:24px 28px; }}
.contacts .row {{ display:flex; align-items:baseline; gap:18px; padding:14px 0; border-bottom:1px solid rgba(12,12,14,0.18); font-family:'JetBrains Mono',monospace; font-size:18px; }}
.contacts .row:last-child {{ border-bottom:none; }}
.contacts .row .label {{ font-weight:700; letter-spacing:0.28em; text-transform:uppercase; color:var(--orange); width:140px; }}
.contacts .row .val {{ font-weight:500; color:var(--ink); }}
</style></head><body>
<div class="slide">
{_e_chrome(brief['series_meta'])}
<div class="content">
  <h1>{h1_html}</h1>
  <p class="body">{body_html}</p>
  <div class="contacts">
    <div class="row"><span class="label">WhatsApp</span><span class="val">+65 9855 8423</span></div>
    <div class="row"><span class="label">Workshop</span><span class="val">Autobay @ Kaki Bukit, #02-61</span></div>
    <div class="row"><span class="label">Web</span><span class="val">therightworkshop.com · link in bio</span></div>
  </div>
</div>
</div></body></html>"""
