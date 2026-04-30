"""Render expansion slides 2..N for each carousel using canonical mode templates.
Slide 1 = the original approved slide.png (untouched). Updates queue accordingly.
"""
import asyncio, json, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import canonical_modes as M
from canonical_briefs import BRIEFS

ROOT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler')
ASSETS = ROOT / "assets"
CANON = ROOT / "carousels/canonical"
QUEUE_FILE = ROOT / "ig_queue.json"

# Layout function name → callable
LAYOUTS = {
    # Mode B
    "b_pullquote": M.b_pullquote, "b_photo_caption": M.b_photo_caption,
    "b_numbered_list": M.b_numbered_list, "b_two_column": M.b_two_column, "b_cta": M.b_cta,
    # Mode A
    "a_pillrise": M.a_pillrise, "a_numbered_card": M.a_numbered_card,
    "a_quote": M.a_quote, "a_cta": M.a_cta,
    # Mode C
    "c_photo_headline": M.c_photo_headline, "c_stat_callout": M.c_stat_callout,
    "c_list_punch": M.c_list_punch, "c_cta": M.c_cta,
    # Mode D
    "d_polaroid_text": M.d_polaroid_text, "d_handwritten_list": M.d_handwritten_list,
    "d_sticky_quote": M.d_sticky_quote, "d_cta": M.d_cta,
    # Mode E
    "e_spec_table": M.e_spec_table, "e_pinned_photo": M.e_pinned_photo,
    "e_data_grid": M.e_data_grid, "e_cta": M.e_cta,
}


def copy_vezel_photos():
    """Copy local Vezel photos into canonical/ so file:// URLs work."""
    src = Path('/tmp/trw-bbtb-mode-mockups')
    for name in ['vezel-clean.png', 'vezel-b.png', 'vezel-c.png', 'vezel-d.png', 'vezel-e.png', 'vezel-bg.png']:
        sp = src / name
        dp = CANON / name
        if sp.exists() and not dp.exists():
            shutil.copy(sp, dp)
            print(f"  copied {name}")


async def render_brief(page, brief_id, mode_name, series_meta, slides_spec):
    """Render slides 2..N for one carousel. Returns list of file paths (slide_2.png onward)."""
    out_dir = ASSETS / brief_id / "slides"
    out_dir.mkdir(parents=True, exist_ok=True)
    brief = {"series_meta": series_meta}
    rendered_paths = []
    for i, (layout_name, kwargs) in enumerate(slides_spec, start=2):
        if layout_name not in LAYOUTS:
            print(f"    ! unknown layout: {layout_name}")
            continue
        try:
            html = LAYOUTS[layout_name](brief, **kwargs)
        except Exception as e:
            print(f"    ! layout {layout_name} failed: {e}")
            continue
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(450)
        out_path = out_dir / f"slide_{i}.png"
        await page.screenshot(path=str(out_path), full_page=False, omit_background=False)
        rel_path = f"assets/{brief_id}/slides/slide_{i}.png"
        rendered_paths.append(rel_path)
    print(f"  ✓ {brief_id} ({mode_name}) — {len(rendered_paths)+1} slides total (1 cover + {len(rendered_paths)} new)")
    return rendered_paths


def update_queue(rendered):
    """Set each carousel's image_paths to [slide.png, slide_2.png, ..., slide_N.png] and type=carousel."""
    q = json.loads(QUEUE_FILE.read_text())
    by_id = {it['id']: it for it in q['pending']}
    flipped = 0
    for brief_id, expansion_paths in rendered.items():
        if brief_id not in by_id:
            print(f"  ! queue entry not found: {brief_id}")
            continue
        e = by_id[brief_id]
        e['type'] = 'carousel'
        # Slide 1 = the original slide.png
        cover_path = f"assets/{brief_id}/slide.png"
        e['image_paths'] = [cover_path] + expansion_paths
        flipped += 1
    QUEUE_FILE.write_text(json.dumps(q, indent=2, ensure_ascii=False))
    print(f"  flipped {flipped} queue entries to type=carousel")


async def main():
    from playwright.async_api import async_playwright
    copy_vezel_photos()
    print(f"\nRendering expansion slides for {len(BRIEFS)} carousels...")
    rendered = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        page = await ctx.new_page()
        for brief_id, (mode_name, series_meta, slides_spec) in BRIEFS.items():
            try:
                paths = await render_brief(page, brief_id, mode_name, series_meta, slides_spec)
                rendered[brief_id] = paths
            except Exception as exc:
                print(f"  ✗ {brief_id} FAILED: {exc}")
        await browser.close()
    print(f"\nRendered expansions for {len(rendered)} / {len(BRIEFS)} carousels.")
    update_queue(rendered)
    print("done.")


if __name__ == "__main__":
    asyncio.run(main())
