"""5 mode template functions. Each takes a `data` dict and returns a list of (filename, html) slide tuples.

Modes: A=Editorial Dark, B=Cream Magazine, C=Poster Bold, D=Polaroid Zine, E=Spec Sheet.
"""

# ============================================================================
# MODE A — EDITORIAL DARK
# ============================================================================
MODE_A_CSS = """
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

LOGO_DARK = '<div class="logo"><span>THE<br/>RIGHT<br/>WS</span></div>'
LOGO_LIGHT = '<div class="logo"><span>THE<br/>RIGHT<br/>WS</span></div>'


def _wrap_a(content, eyebrow_top, footer_left, footer_right, bg_url):
    bg_html = f'<div class="bg" style="background-image:url(\'{bg_url}\');"></div><div class="overlay"></div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_A_CSS}</style></head><body>
{bg_html}
<div class="frame">
  <div class="top-bar">{LOGO_DARK}<div class="eyebrow-top">{eyebrow_top}</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""


def mode_a(d):
    """Editorial Dark — 6 slides: hero, item1, item2, item3, the-tell, cta.
    data: {eyebrow_top, hero_url, chip, sub, title_html, body_html,
           items: [{label, num, title_html, body, watch}, ...3],
           tell_title_html, tell_body_html_1, tell_body_html_2, cta_title_html}"""
    eb = d['eyebrow_top']
    bg = d['hero_url']
    n = len(d.get('items', []))
    total = 3 + n  # hero + items + tell + cta -> actually: hero + N items + tell + cta = N+3

    slides = []

    # SLIDE 1: HERO
    s1 = _wrap_a(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end; padding-bottom:24px;">
  <div style="margin-bottom:16px;"><span class="chip">{d['chip']}</span> <span style="font-size:13px; letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-left:8px;">{d['sub']}</span></div>
  <div class="headline" style="font-size:104px;">{d['title_html']}</div>
  <div class="body-copy" style="margin-top:28px; max-width:880px;">{d['body_html']}</div>
</div>""", eb, "HONEST BY DESIGN", f"01 / {total:02d}  →", bg)
    slides.append(("slide_1.png", s1))

    # MIDDLE: NUMBERED ITEMS
    for i, item in enumerate(d.get('items', []), start=1):
        idx = i + 1
        s = _wrap_a(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:28px;">
  <div class="eyebrow-section">{item['label']}</div>
  <div style="display:grid; grid-template-columns: 200px 1fr; gap:36px; align-items:center;">
    <div class="q-num">{item['num']}</div>
    <div class="headline" style="font-size:78px;">{item['title_html']}</div>
  </div>
  <div class="body-copy" style="max-width:880px; margin-top:8px;">{item['body']}</div>
  <div class="divider"></div>
  <div class="body-copy" style="font-style:italic; opacity:0.85;">{item.get('watch', '')}</div>
</div>""", eb, "HONEST BY DESIGN", f"{idx:02d} / {total:02d}  →", bg)
        slides.append((f"slide_{idx}.png", s))

    # PENULTIMATE: THE TELL
    idx = n + 2
    s_tell = _wrap_a(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
  <div class="eyebrow-section">{d.get('tell_eyebrow','THE TELL')}</div>
  <div class="headline" style="font-size:88px; margin-top:16px;">{d['tell_title_html']}</div>
  <div class="divider"></div>
  <div class="body-copy" style="max-width:880px;">{d['tell_body_html_1']}</div>
  <div class="body-copy" style="margin-top:24px; max-width:880px;">{d['tell_body_html_2']}</div>
</div>""", eb, "HONEST BY DESIGN", f"{idx:02d} / {total:02d}  →", bg)
    slides.append((f"slide_{idx}.png", s_tell))

    # LAST: CTA
    idx = n + 3
    s_cta = _wrap_a(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section">{d.get('cta_eyebrow','BOOK YOUR NEXT SERVICE')}</div>
  <div class="headline" style="font-size:96px; margin-top:8px;">{d['cta_title_html']}</div>
  <div class="divider" style="margin:30px 0 24px;"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;"><div style="width:54px; height:54px; background:#F4A93A; border-radius:999px; color:#1A1410; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">W</div><div><div style="font-weight:800; font-size:22px;">WhatsApp</div><div class="body-copy">+65 8952 1688</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;"><div style="width:54px; height:54px; background:#F4A93A; border-radius:999px; color:#1A1410; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">📍</div><div><div style="font-weight:800; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;"><div style="width:54px; height:54px; background:#F4A93A; border-radius:999px; color:#1A1410; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">↗</div><div><div style="font-weight:800; font-size:22px;">therightworkshop.com</div><div class="body-copy">Link in bio</div></div></div>
</div>""", eb, "THE RIGHT WORKSHOP", "HONEST BY DESIGN", bg)
    slides.append((f"slide_{idx}.png", s_cta))

    return slides


# ============================================================================
# MODE B — CREAM MAGAZINE
# ============================================================================
MODE_B_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Inter:wght@400;500;600;700&display=swap');
* { margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }
body { width:1080px; height:1350px; background:#EFE6D4; font-family:'Inter',sans-serif; color:#1A1A1A; overflow:hidden; position:relative; }
.frame { position:absolute; inset:0; padding:60px 64px; display:flex; flex-direction:column; }
.top-bar { display:flex; justify-content:space-between; align-items:center; height:48px; }
.logo { width:56px; height:56px; background:#1A1A1A; border-radius:999px; display:flex; align-items:center; justify-content:center; color:#EFE6D4; font-weight:700; font-size:11px; line-height:1; text-align:center; flex-shrink:0; }
.logo span { display:block; }
.eyebrow-top { font-size:13px; letter-spacing:3px; font-weight:600; color:#1A1A1A; text-transform:uppercase; }
.bottom-bar { position:absolute; left:64px; right:64px; bottom:48px; display:flex; justify-content:space-between; align-items:center; font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:600; color:#1A1A1A; }
.accent { color:#C73E2C; }
.headline { font-family:'Playfair Display',serif; font-weight:900; font-size:86px; line-height:0.95; letter-spacing:-2px; }
.body-copy { font-family:'Inter',sans-serif; font-size:22px; line-height:1.45; color:#1A1A1A; font-weight:400; }
.body-copy strong { font-weight:600; }
.eyebrow-section { font-size:13px; letter-spacing:3px; font-weight:700; text-transform:uppercase; color:#1A1A1A; margin-bottom:18px; }
.divider { height:1px; background:#1A1A1A; opacity:0.2; margin:22px 0; }
.chip { display:inline-block; padding:8px 14px; background:#C73E2C; color:#EFE6D4; font-size:12px; letter-spacing:2px; font-weight:700; text-transform:uppercase; border-radius:4px; }
"""


def _wrap_b(content, eyebrow_top, footer_left, footer_right):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_B_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO_LIGHT.replace("THE<br/>RIGHT<br/>WS","THE<br/>RIGHT<br/>WORKSHOP")}<div class="eyebrow-top">{eyebrow_top}</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""


def mode_b(d):
    """Cream Magazine — 5 slides: hero (photo card), diagnosis (2-column stat),
       breakdown (timeline-card), cost (light/dark dual cards), cta.
    data: {eyebrow_top, hero_url, chip, hero_eyebrow, hero_title_html, hero_body,
           diag_eyebrow, diag_title_html, diag_left_num, diag_left_body, diag_right_title, diag_right_body, diag_footer,
           tier_eyebrow, tier_title_html, tier_rows: [{range, label, body, color}, ...3],
           cost_eyebrow, cost_title_html, cost_left_label, cost_left_amt, cost_left_body, cost_right_label, cost_right_amt, cost_right_body, cost_note,
           cta_eyebrow, cta_title_html}"""
    eb = d['eyebrow_top']
    series_eb = d.get('series_eyebrow', eb)
    total = 5
    slides = []

    # 1. HERO with photo card
    s1 = _wrap_b(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end; margin-top: 40px;">
  <div style="background: linear-gradient(180deg, transparent 0%, rgba(20,20,20,0.15) 25%, #1f1916 90%), url('{d['hero_url']}') center/cover; height: 720px; border-radius: 18px; position: relative; padding: 48px; display:flex; flex-direction:column; justify-content:flex-end;">
    <div style="position:absolute; top:32px; right:32px;"><span class="chip">{d['chip']}</span></div>
    <div style="color:#EFE6D4;">
      <div class="eyebrow-section" style="color:#EFE6D4; opacity:0.85; margin-bottom:14px;">{d['hero_eyebrow']}</div>
      <div class="headline" style="font-size:78px; color:#EFE6D4; letter-spacing:-1.5px;">{d['hero_title_html']}</div>
    </div>
  </div>
  <div class="body-copy" style="margin-top:28px; max-width:880px;">{d['hero_body']}</div>
</div>""", eb, series_eb, f"01 / {total:02d}  →")
    slides.append(("slide_1.png", s1))

    # 2. DIAGNOSIS
    s2 = _wrap_b(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 30px;">
  <div class="eyebrow-section">{d['diag_eyebrow']}</div>
  <div class="headline" style="font-size:92px;">{d['diag_title_html']}</div>
  <div class="divider"></div>
  <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 18px;">
    <div>
      <div style="font-family:'Playfair Display',serif; font-size:48px; font-weight:700; color:#C73E2C; line-height:1;">{d['diag_left_num']}</div>
      <div class="body-copy" style="margin-top:10px;">{d['diag_left_body']}</div>
    </div>
    <div>
      <div style="font-family:'Playfair Display',serif; font-size:48px; font-weight:700; color:#1A1A1A; line-height:1;">{d['diag_right_title']}</div>
      <div class="body-copy" style="margin-top:10px;">{d['diag_right_body']}</div>
    </div>
  </div>
  <div class="body-copy" style="margin-top:36px;">{d['diag_footer']}</div>
</div>""", eb, series_eb, f"02 / {total:02d}  →")
    slides.append(("slide_2.png", s2))

    # 3. TIMELINE CARD (3 tiers)
    rows_html = ""
    for r in d['tier_rows']:
        rows_html += f"""<div style="display:grid; grid-template-columns: 130px 1fr; gap:20px; align-items:center; margin-bottom:22px;">
      <div style="font-family:'Playfair Display',serif; font-size:42px; font-weight:900; color:{r['color']}; white-space:nowrap;">{r['range']}</div>
      <div><div style="font-weight:700; font-size:18px; letter-spacing:1px; text-transform:uppercase; color:{r['color']};">{r['label']}</div><div style="margin-top:4px; font-size:20px;">{r['body']}</div></div>
    </div>"""
    s3 = _wrap_b(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 30px;">
  <div class="eyebrow-section">{d['tier_eyebrow']}</div>
  <div class="headline" style="font-size:80px; margin-bottom: 36px;">{d['tier_title_html']}</div>
  <div style="background:#1A1A1A; border-radius:14px; padding:32px; color:#EFE6D4;">{rows_html}</div>
</div>""", eb, series_eb, f"03 / {total:02d}  →")
    slides.append(("slide_3.png", s3))

    # 4. COST SPLIT
    s4 = _wrap_b(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 30px;">
  <div class="eyebrow-section">{d['cost_eyebrow']}</div>
  <div class="headline" style="font-size:76px; margin-bottom: 32px;">{d['cost_title_html']}</div>
  <div style="display:grid; grid-template-columns: 1fr 1fr; gap:24px;">
    <div style="background:#FFFFFF; border:1.5px solid #1A1A1A; border-radius:14px; padding:32px;">
      <div style="font-size:13px; letter-spacing:2px; font-weight:700; text-transform:uppercase; color:#1A1A1A;">{d['cost_left_label']}</div>
      <div style="font-family:'Playfair Display',serif; font-size:88px; font-weight:900; color:#1A1A1A; line-height:1; margin:12px 0;">{d['cost_left_amt']}</div>
      <div class="body-copy" style="font-size:18px;">{d['cost_left_body']}</div>
    </div>
    <div style="background:#1A1A1A; border-radius:14px; padding:32px; color:#EFE6D4;">
      <div style="font-size:13px; letter-spacing:2px; font-weight:700; text-transform:uppercase; color:#F4A93A;">{d['cost_right_label']}</div>
      <div style="font-family:'Playfair Display',serif; font-size:88px; font-weight:900; color:#EFE6D4; line-height:1; margin:12px 0;">{d['cost_right_amt']}</div>
      <div class="body-copy" style="font-size:18px; color:#EFE6D4;">{d['cost_right_body']}</div>
    </div>
  </div>
  <div class="body-copy" style="margin-top:32px; font-style: italic;">{d['cost_note']}</div>
</div>""", eb, series_eb, f"04 / {total:02d}  →")
    slides.append(("slide_4.png", s4))

    # 5. CTA
    s5 = _wrap_b(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; margin-top: 20px;">
  <div class="eyebrow-section">{d['cta_eyebrow']}</div>
  <div class="headline" style="font-size:96px;">{d['cta_title_html']}</div>
  <div class="divider" style="margin:36px 0 28px;"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:18px; align-items:center; margin-bottom:20px;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:22px;">W</div><div><div style="font-weight:700; font-size:22px;">WhatsApp</div><div class="body-copy">+65 8952 1688</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:18px; align-items:center; margin-bottom:20px;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:22px;">📍</div><div><div style="font-weight:700; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:18px; align-items:center;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:18px;">↗</div><div><div style="font-weight:700; font-size:22px;">Read the full guide</div><div class="body-copy">therightworkshop.com / link in bio</div></div></div>
</div>""", eb, "THE RIGHT WORKSHOP", "HONEST BY DESIGN")
    slides.append(("slide_5.png", s5))

    return slides


# ============================================================================
# MODE C — POSTER BOLD
# ============================================================================
MODE_C_CSS = """
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


def _wrap_c(content, eyebrow_top, footer_left, footer_right):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_C_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO_DARK}<div class="eyebrow-top">{eyebrow_top}</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""


def mode_c(d):
    """Poster Bold — 6 slides: hero, timeline, cost split, list, rule, cta.
    data: {eyebrow_top, hero_url, hero_chip, hero_eyebrow, hero_title_html, hero_body,
           tl_eyebrow, tl_title_html, tl_rows: [{label, label_body, body, accent}, ...3],
           cost_eyebrow, cost_title_html, cost_left_label, cost_left_amt, cost_left_body, cost_right_label, cost_right_amt, cost_right_body, cost_note,
           list_eyebrow, list_title_html, list_items: [{n, body}, ...4],
           rule_eyebrow, rule_title_html, rule_sub, rule_body_1, rule_body_2,
           cta_eyebrow, cta_title_html}"""
    eb = d['eyebrow_top']
    total = 6
    slides = []

    # 1 HERO
    s1 = _wrap_c(f"""
<div style="margin-top:24px; height:480px; background:linear-gradient(180deg, rgba(15,15,18,0.30) 0%, rgba(15,15,18,0.45) 60%, rgba(15,15,18,0.92) 100%), url('{d['hero_url']}') center/cover; border-radius:14px; position:relative;">
  <div style="position:absolute; top:32px; right:32px;"><span class="eyebrow-top" style="background:#0F0F12; color:#E96A2C; border:1px solid #E96A2C;">{d['hero_chip']}</span></div>
</div>
<div style="margin-top:36px;">
  <div class="eyebrow-section">{d['hero_eyebrow']}</div>
  <div class="headline" style="font-size:108px;">{d['hero_title_html']}</div>
  <div class="body-copy" style="margin-top:24px; max-width:880px;">{d['hero_body']}</div>
</div>""", eb, eb, f"01 / {total:02d}  →")
    slides.append(("slide_1.png", s1))

    # 2 TIMELINE 3-tier
    rows = ""
    for r in d['tl_rows']:
        bg = "#E96A2C" if r.get('accent') else "#1A1A1F"
        col = "#0F0F12" if r.get('accent') else "#F2EBDD"
        col_label = "#0F0F12" if r.get('accent') else "#E96A2C"
        rows += f"""<div style="display:grid; grid-template-columns: 220px 1fr; gap:24px; align-items:center; padding:20px 24px; background:{bg}; color:{col}; border-radius:12px;">
      <div class="stat-big" style="font-size:64px; color:{col}; white-space:nowrap;">{r['label']}</div>
      <div><div style="font-weight:800; font-size:18px; color:{col_label}; letter-spacing:1.5px; text-transform:uppercase;">{r['label_body']}</div><div class="body-copy" style="margin-top:4px; color:{col};">{r['body']}</div></div>
    </div>"""
    s2 = _wrap_c(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:24px;">
  <div class="eyebrow-section">{d['tl_eyebrow']}</div>
  <div class="headline" style="font-size:90px;">{d['tl_title_html']}</div>
  <div style="margin-top:18px; display:flex; flex-direction:column; gap:18px;">{rows}</div>
</div>""", eb, eb, f"02 / {total:02d}  →")
    slides.append(("slide_2.png", s2))

    # 3 COST SPLIT
    s3 = _wrap_c(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:30px;">
  <div class="eyebrow-section">{d['cost_eyebrow']}</div>
  <div class="headline" style="font-size:80px;">{d['cost_title_html']}</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:14px;">
    <div style="background:#1A1A1F; border-radius:12px; padding:28px;"><div style="font-size:13px; letter-spacing:2px; font-weight:800; text-transform:uppercase; color:#F2EBDD; opacity:0.7;">{d['cost_left_label']}</div><div class="stat-big" style="margin-top:8px; color:#F2EBDD;">{d['cost_left_amt']}</div><div class="body-copy" style="margin-top:8px; font-size:18px; opacity:0.85;">{d['cost_left_body']}</div></div>
    <div style="background:#E96A2C; color:#0F0F12; border-radius:12px; padding:28px;"><div style="font-size:13px; letter-spacing:2px; font-weight:900; text-transform:uppercase; color:#0F0F12;">{d['cost_right_label']}</div><div class="stat-big" style="margin-top:8px; color:#0F0F12;">{d['cost_right_amt']}</div><div class="body-copy" style="margin-top:8px; font-size:18px; color:#0F0F12;">{d['cost_right_body']}</div></div>
  </div>
  <div class="body-copy" style="text-align:center; opacity:0.85; font-style:italic;">{d['cost_note']}</div>
</div>""", eb, eb, f"03 / {total:02d}  →")
    slides.append(("slide_3.png", s3))

    # 4 LIST
    items = ""
    for it in d['list_items']:
        items += f"""<div style="display:flex; gap:18px; align-items:flex-start;"><div style="flex-shrink:0; width:48px; height:48px; background:#E96A2C; color:#0F0F12; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">{it['n']}</div><div class="body-copy">{it['body']}</div></div>"""
    s4 = _wrap_c(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:24px;">
  <div class="eyebrow-section">{d['list_eyebrow']}</div>
  <div class="headline" style="font-size:84px;">{d['list_title_html']}</div>
  <div style="display:flex; flex-direction:column; gap:14px; margin-top:14px;">{items}</div>
</div>""", eb, eb, f"04 / {total:02d}  →")
    slides.append(("slide_4.png", s4))

    # 5 RULE
    s5 = _wrap_c(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:24px;">
  <div class="eyebrow-section">{d['rule_eyebrow']}</div>
  <div class="headline" style="font-size:120px;">{d['rule_title_html']}<br/><span style="font-size:60px; font-weight:700; color:#F2EBDD; opacity:0.7; letter-spacing:0; text-transform:none; font-style:italic;">{d['rule_sub']}</span></div>
  <div class="divider"></div>
  <div class="body-copy" style="max-width:880px;">{d['rule_body_1']}</div>
  <div class="body-copy" style="max-width:880px;">{d['rule_body_2']}</div>
</div>""", eb, eb, f"05 / {total:02d}  →")
    slides.append(("slide_5.png", s5))

    # 6 CTA
    s6 = _wrap_c(f"""
<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section">{d['cta_eyebrow']}</div>
  <div class="headline" style="font-size:108px;">{d['cta_title_html']}</div>
  <div class="divider"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;"><div style="width:54px; height:54px; background:#E96A2C; border-radius:999px; color:#0F0F12; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:22px;">W</div><div><div style="font-weight:900; font-size:22px;">WhatsApp</div><div class="body-copy">+65 8952 1688</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:18px;"><div style="width:54px; height:54px; background:#E96A2C; border-radius:999px; color:#0F0F12; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">📍</div><div><div style="font-weight:900; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;"><div style="width:54px; height:54px; background:#E96A2C; border-radius:999px; color:#0F0F12; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px;">↗</div><div><div style="font-weight:900; font-size:22px;">therightworkshop.com</div><div class="body-copy">Link in bio</div></div></div>
</div>""", eb, "THE RIGHT WORKSHOP", "HONEST BY DESIGN")
    slides.append(("slide_6.png", s6))

    return slides


# ============================================================================
# MODE D — POLAROID ZINE
# ============================================================================
MODE_D_CSS = """
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


def _wrap_d(content, eyebrow_top, footer_left, footer_right):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_D_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO_LIGHT}<div class="eyebrow-top">{eyebrow_top}</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""


def mode_d(d):
    """Polaroid Zine — 6 slides: hero polaroid+sticky, polaroid-grid (3), sticky-invoice, list, lesson, cta.
    Trimmed from 7 to 6 to keep authoring scope manageable.
    data: {eyebrow_top, hero_photo, hero_caption, hero_sticky_html, hero_eyebrow, hero_title_html, hero_body,
           grid_eyebrow, grid_title_html, grid_items: [{label, sublabel, color}, ...3], grid_body,
           inv_eyebrow, inv_title_html, inv_rows: [{label, amt}, ...], inv_total_amt, inv_body,
           list_eyebrow, list_title_html, list_items: [{n, body}, ...4],
           lesson_eyebrow, lesson_title_html, lesson_body_1, lesson_body_2,
           cta_eyebrow, cta_title_html}"""
    eb = d['eyebrow_top']
    total = 6
    slides = []

    # 1 HERO polaroid + sticky
    s1 = _wrap_d(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:flex-start;">
  <div style="position:relative; height:480px;">
    <div class="polaroid" style="width:560px; transform:rotate(-3deg); position:absolute; left:0; top:0;">
      <div class="polaroid-photo" style="background-image:url('{d['hero_photo']}');"></div>
      <div class="polaroid-caption">{d['hero_caption']}</div>
    </div>
    <div class="sticky" style="width:300px; position:absolute; right:8px; top:120px;">
      <div class="handwriting">{d['hero_sticky_html']}</div>
    </div>
  </div>
  <div style="margin-top:36px;">
    <div class="eyebrow-section">{d['hero_eyebrow']}</div>
    <div class="headline" style="font-size:78px;">{d['hero_title_html']}</div>
    <div class="body-mono" style="margin-top:18px;">{d['hero_body']}</div>
  </div>
</div>""", eb, "THE RIGHT WORKSHOP", f"01 / {total:02d}  →")
    slides.append(("slide_1.png", s1))

    # 2 POLAROID GRID (3)
    grid_html = ""
    for i, it in enumerate(d['grid_items']):
        rot = [-2, 1.5, -1][i]
        bg = it.get('color', '#1A1A1A')
        text_col = "#FFFFFF" if bg != '#FFFFFF' else "#1A1A1A"
        grid_html += f"""<div class="polaroid" style="transform:rotate({rot}deg); padding:10px 10px 36px;">
      <div style="background:{bg}; height:200px; display:flex; align-items:center; justify-content:center; color:{text_col}; font-family:'Caveat',cursive; font-size:30px; padding:14px; text-align:center;">{it['label']}</div>
      <div style="font-family:'Caveat',cursive; font-size:18px; text-align:center; padding-top:10px;">{it['sublabel']}</div>
    </div>"""
    s2 = _wrap_d(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column;">
  <div class="eyebrow-section">{d['grid_eyebrow']}</div>
  <div class="headline" style="font-size:62px; margin-bottom:30px;">{d['grid_title_html']}</div>
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:18px;">{grid_html}</div>
  <div class="body-mono" style="margin-top:30px;">{d['grid_body']}</div>
</div>""", eb, "THE RIGHT WORKSHOP", f"02 / {total:02d}  →")
    slides.append(("slide_2.png", s2))

    # 3 STICKY INVOICE
    rows = ""
    for r in d['inv_rows']:
        rows += f"""<div style="display:flex; justify-content:space-between; border-bottom:1px dashed #1A1A1A; padding-bottom:8px; margin-bottom:8px;"><span>{r['label']}</span><span>{r['amt']}</span></div>"""
    s3 = _wrap_d(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:32px;">
  <div class="eyebrow-section">{d['inv_eyebrow']}</div>
  <div class="headline" style="font-size:72px;">{d['inv_title_html']}</div>
  <div class="sticky" style="width:560px; transform:rotate(-1deg); padding:32px 36px;">
    <div class="handwriting" style="font-size:30px;">{rows}<div style="display:flex; justify-content:space-between; padding-top:8px; font-weight:700;"><span>TOTAL</span><span>{d['inv_total_amt']}</span></div></div>
  </div>
  <div class="body-mono">{d['inv_body']}</div>
</div>""", eb, "THE RIGHT WORKSHOP", f"03 / {total:02d}  →")
    slides.append(("slide_3.png", s3))

    # 4 LIST
    items = ""
    for it in d['list_items']:
        items += f"""<div style="display:grid; grid-template-columns: 56px 1fr; gap:18px; align-items:flex-start;"><div class="handwriting" style="font-size:38px; color:#C73E2C; font-weight:700;">{it['n']}</div><div class="body-mono">{it['body']}</div></div>"""
    s4 = _wrap_d(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:22px;">
  <div class="eyebrow-section">{d['list_eyebrow']}</div>
  <div class="headline" style="font-size:58px;">{d['list_title_html']}</div>
  <div style="display:flex; flex-direction:column; gap:14px; margin-top:8px;">{items}</div>
</div>""", eb, "THE RIGHT WORKSHOP", f"04 / {total:02d}  →")
    slides.append(("slide_4.png", s4))

    # 5 LESSON
    s5 = _wrap_d(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:22px;">
  <div class="eyebrow-section">{d['lesson_eyebrow']}</div>
  <div class="headline" style="font-size:96px;">{d['lesson_title_html']}</div>
  <div class="body-mono" style="max-width:880px;">{d['lesson_body_1']}</div>
  <div class="body-mono" style="max-width:880px; font-style:italic; opacity:0.85;">{d['lesson_body_2']}</div>
</div>""", eb, "THE RIGHT WORKSHOP", f"05 / {total:02d}  →")
    slides.append(("slide_5.png", s5))

    # 6 CTA
    s6 = _wrap_d(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section">{d['cta_eyebrow']}</div>
  <div class="headline" style="font-size:88px;">{d['cta_title_html']}</div>
  <div style="height:1px; background:#1A1A1A; opacity:0.2; margin:30px 0 20px;"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EDE3CD; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:22px;">W</div><div><div style="font-weight:800; font-size:22px;">WhatsApp</div><div class="body-mono">+65 8952 1688</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EDE3CD; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">📍</div><div><div style="font-weight:800; font-size:22px;">Workshop</div><div class="body-mono">Autobay @ Kaki Bukit, #02-61</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EDE3CD; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">↗</div><div><div style="font-weight:800; font-size:22px;">therightworkshop.com</div><div class="body-mono">Link in bio</div></div></div>
</div>""", eb, "THE RIGHT WORKSHOP", "HONEST BY DESIGN")
    slides.append(("slide_6.png", s6))

    return slides


# ============================================================================
# MODE E — SPEC SHEET
# ============================================================================
MODE_E_CSS = """
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


def _wrap_e(content, eyebrow_top, footer_left, footer_right):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{MODE_E_CSS}</style></head><body>
<div class="frame">
  <div class="top-bar">{LOGO_DARK}<div class="eyebrow-top">{eyebrow_top}</div></div>
  {content}
</div>
<div class="bottom-bar"><span>{footer_left}</span><span>{footer_right}</span></div>
</body></html>"""


def mode_e(d):
    """Spec Sheet — 6 slides: diagram (with pins), spec table, matrix grid, list flow, table-2, cta.
    Trimmed from 7 to 6.
    data: {eyebrow_top, file_meta, file_subtitle, hero_url,
           pins: [{x,y,label,desc}, ...4],
           pic_eyebrow, pic_title_html, pic_body,
           tab1_eyebrow, tab1_title_html, tab1_cols: [...4], tab1_rows: [{key, c1, c2, c3, c4}, ...],
           grid_eyebrow, grid_title_html, grid_cells: [{label, big, body, accent}, ...4],
           list_eyebrow, list_title_html, list_items: [{n, body}, ...4],
           tab2_eyebrow, tab2_title_html, tab2_cols, tab2_rows,
           cta_eyebrow, cta_title_html}"""
    eb = d['eyebrow_top']
    total = 6
    slides = []

    # 1 DIAGRAM with PINS + headline
    pins_html = ""
    for p in d['pins']:
        pins_html += f"""<div class="label-pin" style="{p.get('pos','top:30px;left:50px;')}">{p['label']}</div>
    <div style="position:absolute; {p.get('desc_pos','top:30px;left:96px;')} padding:4px 10px; background:#1A1A1A; color:#EFE6D4; font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:1.5px; font-weight:700;">{p['desc']}</div>"""
    s1 = _wrap_e(f"""
<div style="margin-top:24px;">
  <div style="display:flex; gap:18px; font-size:11px; letter-spacing:2px; font-weight:800; text-transform:uppercase; color:#1A1A1A; opacity:0.7; margin-bottom:8px;">{d['file_meta']}</div>
  <div style="font-weight:700; font-size:20px;">{d['file_subtitle']}</div>
  <div style="margin-top:14px; height:340px; background:url('{d['hero_url']}') center/cover; border-radius:6px; position:relative;">
    {pins_html}
  </div>
  <div style="margin-top:30px;">
    <div class="eyebrow-section" style="opacity:0.7; margin-bottom:14px;">{d['pic_eyebrow']}</div>
    <div class="headline" style="font-size:74px;">{d['pic_title_html']}</div>
    <div class="body-copy" style="margin-top:20px; max-width:960px;">{d['pic_body']}</div>
  </div>
</div>""", eb, eb.replace("DECODED","DECODED"), f"01 / {total:02d}  ↗")
    slides.append(("slide_1.png", s1))

    # 2 SPEC TABLE 1
    head = "".join(f"<th>{c}</th>" for c in d['tab1_cols'])
    body = ""
    for r in d['tab1_rows']:
        body += f"<tr><td>{r['key']}</td><td>{r['c1']}</td><td>{r['c2']}</td><td>{r['c3']}</td><td>{r['c4']}</td></tr>"
    s2 = _wrap_e(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:flex-start;">
  <div class="eyebrow-section" style="color:#C73E2C;">{d['tab1_eyebrow']}</div>
  <div class="headline" style="font-size:60px; margin-top:14px;">{d['tab1_title_html']}</div>
  <table class="spec-table" style="margin-top:32px;">
    <thead><tr><th></th>{head}</tr></thead>
    <tbody>{body}</tbody>
  </table>
</div>""", eb, eb, f"02 / {total:02d}  ↗")
    slides.append(("slide_2.png", s2))

    # 3 MATRIX GRID 2x2
    cells = ""
    for c in d['grid_cells']:
        if c.get('accent'):
            cells += f"""<div style="background:#1A1A1A; color:#EFE6D4; border-radius:8px; padding:24px;"><div class="eyebrow-section" style="color:#F4A93A;">{c['label']}</div><div style="font-family:'JetBrains Mono',mono; font-size:42px; font-weight:800; margin-top:8px; color:#C73E2C;">{c['big']}</div><div class="body-copy" style="margin-top:8px; font-size:19px; color:#EFE6D4;">{c['body']}</div></div>"""
        else:
            cells += f"""<div style="background:#FFFFFF; border:1.5px solid #1A1A1A; border-radius:8px; padding:24px;"><div class="eyebrow-section" style="color:#C73E2C;">{c['label']}</div><div style="font-family:'JetBrains Mono',mono; font-size:42px; font-weight:800; margin-top:8px;">{c['big']}</div><div class="body-copy" style="margin-top:8px; font-size:19px;">{c['body']}</div></div>"""
    s3 = _wrap_e(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:24px;">
  <div class="eyebrow-section" style="color:#C73E2C;">{d['grid_eyebrow']}</div>
  <div class="headline" style="font-size:60px;">{d['grid_title_html']}</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:8px;">{cells}</div>
</div>""", eb, eb, f"03 / {total:02d}  ↗")
    slides.append(("slide_3.png", s3))

    # 4 LIST FLOW
    items = ""
    for it in d['list_items']:
        items += f"""<div style="display:grid; grid-template-columns:60px 1fr; gap:14px; padding:14px 0; border-bottom:1px dashed #1A1A1A;"><div style="font-weight:800; color:#C73E2C; font-family:'JetBrains Mono',mono; font-size:18px;">[{it['n']}]</div><div style="font-family:'JetBrains Mono',mono; font-size:18px; line-height:1.6;">{it['body']}</div></div>"""
    s4 = _wrap_e(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:22px;">
  <div class="eyebrow-section" style="color:#C73E2C;">{d['list_eyebrow']}</div>
  <div class="headline" style="font-size:62px;">{d['list_title_html']}</div>
  <div style="margin-top:10px;">{items}</div>
</div>""", eb, eb, f"04 / {total:02d}  ↗")
    slides.append(("slide_4.png", s4))

    # 5 SPEC TABLE 2
    head2 = "".join(f"<th>{c}</th>" for c in d['tab2_cols'])
    body2 = ""
    for r in d['tab2_rows']:
        cells = "".join(f"<td>{r.get(f'c{i+1}','')}</td>" for i in range(len(d['tab2_cols'])))
        body2 += f"<tr><td>{r['key']}</td>{cells}</tr>"
    s5 = _wrap_e(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; gap:24px;">
  <div class="eyebrow-section" style="color:#C73E2C;">{d['tab2_eyebrow']}</div>
  <div class="headline" style="font-size:62px;">{d['tab2_title_html']}</div>
  <table class="spec-table" style="margin-top:14px;">
    <thead><tr><th></th>{head2}</tr></thead>
    <tbody>{body2}</tbody>
  </table>
</div>""", eb, eb, f"05 / {total:02d}  ↗")
    slides.append(("slide_5.png", s5))

    # 6 CTA
    s6 = _wrap_e(f"""
<div style="margin-top:32px; flex:1; display:flex; flex-direction:column; justify-content:center; gap:14px;">
  <div class="eyebrow-section" style="color:#C73E2C;">{d['cta_eyebrow']}</div>
  <div class="headline" style="font-size:88px;">{d['cta_title_html']}</div>
  <div class="divider"></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:22px;">W</div><div><div style="font-weight:800; font-size:22px;">WhatsApp</div><div class="body-copy">+65 8952 1688</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center; margin-bottom:14px;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">📍</div><div><div style="font-weight:800; font-size:22px;">Workshop</div><div class="body-copy">Autobay @ Kaki Bukit, #02-61</div></div></div>
  <div style="display:grid; grid-template-columns: auto 1fr; gap:16px; align-items:center;"><div style="width:54px; height:54px; background:#1A1A1A; border-radius:999px; color:#EFE6D4; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px;">↗</div><div><div style="font-weight:800; font-size:22px;">therightworkshop.com</div><div class="body-copy">Link in bio</div></div></div>
</div>""", eb, "THE RIGHT WORKSHOP", "HONEST BY DESIGN")
    slides.append(("slide_6.png", s6))

    return slides
