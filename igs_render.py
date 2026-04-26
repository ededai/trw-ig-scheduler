#!/usr/bin/env python3
"""
TRW IGS (Instagram Story) renderer.

Takes a TRW blog post URL + variant (A/B/C) and produces a 1080x1920 PNG ready
to publish via post_instagram.py --story.

Pipeline:
  1. Playwright loads the blog URL, screenshots it at 1080x1920 (background).
  2. Loads the IGS template HTML with the screenshot embedded + variant text
     substituted.
  3. Screenshots the rendered template at 1080x1920 (final IGS).

Usage:
  python3 igs_render.py \
    --blog-url https://therightworkshop.com/10-signs-trustworthy-mechanic-singapore/ \
    --variant A \
    --title "10 Signs of a Trustworthy Mechanic in Singapore" \
    --sub "Most drivers in SG can't tell a good mechanic from a bad one." \
    --output /tmp/igs_a.png

Variants:
  A — Editorial Teaser (title + sub, orange eyebrow tag "NEW ON THE BLOG")
  B — Question Hook (orange wash bg, conversational question)
  C — Quote Pull (heavy dark scrim, italic quote)

Requires: playwright (pip install playwright && playwright install chromium)
"""

import argparse
import asyncio
import base64
import html
import sys
import tempfile
from pathlib import Path

VARIANT_CONFIG = {
    "A": {
        "eyebrow_text": "NEW ON THE BLOG",
        "eyebrow_bg": "#FF6B00",
        "eyebrow_color": "#fff",
        "scrim": "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.35) 30%, rgba(0,0,0,0.65) 70%, rgba(0,0,0,0.85) 100%)",
        "title_size": "78px",
        "title_style": "normal",
    },
    "B": {
        "eyebrow_text": "QUICK QUESTION",
        "eyebrow_bg": "#fff",
        "eyebrow_color": "#FF6B00",
        "scrim": "linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(255,107,0,0.55) 100%)",
        "title_size": "96px",
        "title_style": "normal",
    },
    "C": {
        "eyebrow_text": "FROM THE BLOG",
        "eyebrow_bg": "#FF6B00",
        "eyebrow_color": "#fff",
        "scrim": "rgba(0,0,0,0.78)",
        "title_size": "108px",
        "title_style": "italic",
    },
}

TEMPLATE_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body {
    width: 1080px;
    height: 1920px;
    background: #000;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    overflow: hidden;
  }
  .frame {
    position: relative;
    width: 1080px;
    height: 1920px;
  }
  .bg {
    position: absolute;
    inset: 0;
    background-image: url('{BG_DATA_URL}');
    background-size: cover;
    background-position: top center;
    background-repeat: no-repeat;
  }
  .scrim {
    position: absolute;
    inset: 0;
    background: {SCRIM};
  }
  .overlay {
    position: absolute;
    inset: 0;
    padding: 285px 84px 270px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    z-index: 10;
  }
  .eyebrow {
    background: {EYEBROW_BG};
    color: {EYEBROW_COLOR};
    font-size: 33px;
    font-weight: 700;
    letter-spacing: 9px;
    text-transform: uppercase;
    padding: 18px 42px;
    border-radius: 12px;
    align-self: center;
    display: inline-block;
  }
  .mid {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 42px;
    padding: 60px 0;
  }
  .title {
    color: #fff;
    font-size: {TITLE_SIZE};
    font-style: {TITLE_STYLE};
    font-weight: 900;
    line-height: 1.08;
    text-shadow: 0 6px 36px rgba(0,0,0,0.55);
  }
  .sub {
    color: rgba(255,255,255,0.95);
    font-size: 42px;
    line-height: 1.4;
    font-weight: 500;
    text-shadow: 0 3px 18px rgba(0,0,0,0.6);
    padding: 0 24px;
  }
  .cta {
    align-self: center;
    color: #fff;
    background: rgba(0,0,0,0.55);
    padding: 39px 51px;
    border-radius: 36px;
    font-size: 36px;
    font-weight: 700;
    letter-spacing: 1.2px;
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
    border: 3px solid rgba(255,255,255,0.18);
  }
  .cta strong { color: #FF8A33; }
</style>
</head><body>
  <div class="frame">
    <div class="bg"></div>
    <div class="scrim"></div>
    <div class="overlay">
      <div class="eyebrow">{EYEBROW_TEXT}</div>
      <div class="mid">
        <div class="title">{TITLE}</div>
        <div class="sub">{SUB}</div>
      </div>
      <div class="cta">🔗 <strong>Link in bio</strong> &nbsp;·&nbsp; therightworkshop.com</div>
    </div>
  </div>
</body></html>
"""


async def screenshot_blog(blog_url: str, out_path: Path) -> None:
    """Screenshot the blog post URL at 1080x1920 (top-aligned, full visible viewport)."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": 1080, "height": 1920})
        page = await context.new_page()
        await page.goto(blog_url, wait_until="networkidle", timeout=60000)
        # Pause briefly for fonts/images to settle
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(out_path), full_page=False)
        await browser.close()


async def render_template(bg_path: Path, variant: str, title: str, sub: str,
                          out_path: Path) -> None:
    """Render the IGS template with substituted vars and screenshot to out_path."""
    cfg = VARIANT_CONFIG[variant]
    bg_bytes = bg_path.read_bytes()
    bg_b64 = base64.b64encode(bg_bytes).decode("ascii")
    bg_data_url = f"data:image/png;base64,{bg_b64}"

    html_str = TEMPLATE_HTML
    html_str = html_str.replace("{BG_DATA_URL}", bg_data_url)
    html_str = html_str.replace("{SCRIM}", cfg["scrim"])
    html_str = html_str.replace("{EYEBROW_BG}", cfg["eyebrow_bg"])
    html_str = html_str.replace("{EYEBROW_COLOR}", cfg["eyebrow_color"])
    html_str = html_str.replace("{EYEBROW_TEXT}", cfg["eyebrow_text"])
    html_str = html_str.replace("{TITLE_SIZE}", cfg["title_size"])
    html_str = html_str.replace("{TITLE_STYLE}", cfg["title_style"])
    html_str = html_str.replace("{TITLE}", html.escape(title))
    html_str = html_str.replace("{SUB}", html.escape(sub))

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
        f.write(html_str)
        tmp_html = Path(f.name)

    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(viewport={"width": 1080, "height": 1920})
            page = await context.new_page()
            await page.goto(f"file://{tmp_html}", wait_until="load")
            await page.wait_for_timeout(500)
            await page.screenshot(path=str(out_path), full_page=False, omit_background=False)
            await browser.close()
    finally:
        tmp_html.unlink(missing_ok=True)


async def main_async(args):
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.bg_image:
        bg_path = Path(args.bg_image).resolve()
        if not bg_path.exists():
            print(f"ERROR: bg-image not found: {bg_path}")
            sys.exit(1)
    else:
        bg_path = out.parent / f"{out.stem}_bg.png"
        print(f"Screenshotting blog: {args.blog_url}")
        await screenshot_blog(args.blog_url, bg_path)
        print(f"  -> {bg_path}")

    print(f"Rendering variant {args.variant}: {args.title[:60]}")
    await render_template(bg_path, args.variant, args.title, args.sub, out)
    print(f"  -> {out}")


def main():
    p = argparse.ArgumentParser(description="Render TRW IGS PNG from a blog post URL")
    p.add_argument("--blog-url", required=True, help="Live URL of the blog post")
    p.add_argument("--variant", choices=["A", "B", "C"], required=True)
    p.add_argument("--title", required=True, help="Headline text on the IGS")
    p.add_argument("--sub", default="", help="Subtitle / teaser text")
    p.add_argument("--output", required=True, help="Path to write the final 1080x1920 PNG")
    p.add_argument("--bg-image", default=None, help="Optional pre-captured background PNG (skips re-screenshotting)")
    args = p.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
