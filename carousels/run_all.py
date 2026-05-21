"""Render all 16 new carousels + flip queue entries from type=single to type=carousel.

Reads briefs.py, calls modes.py functions, renders via Playwright, updates ig_queue.json.
"""
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from briefs import BRIEFS
import modes

ROOT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler')
ASSETS = ROOT / "assets"
QUEUE_FILE = ROOT / "ig_queue.json"

MODE_FUNCS = {
    "mode_a": modes.mode_a,
    "mode_b": modes.mode_b,
    "mode_c": modes.mode_c,
    "mode_d": modes.mode_d,
    "mode_e": modes.mode_e,
}


async def render_brief(page, brief_id, mode_name, data):
    """Render all slides for one brief."""
    out_dir = ASSETS / brief_id / "slides"
    out_dir.mkdir(parents=True, exist_ok=True)
    func = MODE_FUNCS[mode_name]
    slides = func(data)
    rendered_paths = []
    for filename, html in slides:
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(400)
        out_path = out_dir / filename
        await page.screenshot(path=str(out_path), full_page=False, omit_background=False)
        rel_path = f"assets/{brief_id}/slides/{filename}"
        rendered_paths.append(rel_path)
    print(f"  ✓ {brief_id} — {len(slides)} slides ({mode_name})")
    return rendered_paths


def update_queue(rendered):
    """Flip type=single → type=carousel and replace image_paths with the rendered slide arrays.
    Skips IDs that don't exist or are already carousels."""
    q = json.loads(QUEUE_FILE.read_text())
    by_id = {it['id']: it for it in q['pending']}
    flipped = 0
    for brief_id, paths in rendered.items():
        if brief_id not in by_id:
            print(f"  ! queue entry not found: {brief_id}")
            continue
        e = by_id[brief_id]
        e['type'] = 'carousel'
        e['image_paths'] = paths
        flipped += 1
    QUEUE_FILE.write_text(json.dumps(q, indent=2, ensure_ascii=False))
    print(f"  flipped {flipped} queue entries to type=carousel")


async def main():
    from playwright.async_api import async_playwright
    print(f"Rendering {len(BRIEFS)} carousels...")
    rendered = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        page = await ctx.new_page()
        for brief_id, (mode_name, data) in BRIEFS.items():
            try:
                paths = await render_brief(page, brief_id, mode_name, data)
                rendered[brief_id] = paths
            except Exception as exc:
                print(f"  ✗ {brief_id} FAILED: {exc}")
        await browser.close()

    print(f"\nRendered {len(rendered)} / {len(BRIEFS)} carousels.")
    print("Updating queue...")
    update_queue(rendered)

    # Also update the 5 prototypes that were already rendered to type=carousel
    proto_paths = {
        "newseries-wl-mode-b-2026-05-02-11":  ["assets/newseries-wl-mode-b-2026-05-02-11/slides/slide_1.png","assets/newseries-wl-mode-b-2026-05-02-11/slides/slide_2.png","assets/newseries-wl-mode-b-2026-05-02-11/slides/slide_3.png","assets/newseries-wl-mode-b-2026-05-02-11/slides/slide_4.png","assets/newseries-wl-mode-b-2026-05-02-11/slides/slide_5.png"],
        "newseries-st-mode-a-2026-05-02-15":  [f"assets/newseries-st-mode-a-2026-05-02-15/slides/slide_{i}.png" for i in range(1,7)],
        "newseries-cow-mode-c-2026-05-04-20": [f"assets/newseries-cow-mode-c-2026-05-04-20/slides/slide_{i}.png" for i in range(1,7)],
        "newseries-cow-mode-d-2026-05-06-20": [f"assets/newseries-cow-mode-d-2026-05-06-20/slides/slide_{i}.png" for i in range(1,8)],
        "newseries-wl-mode-e-2026-05-08-11":  [f"assets/newseries-wl-mode-e-2026-05-08-11/slides/slide_{i}.png" for i in range(1,8)],
    }
    update_queue(proto_paths)
    print("done.")


if __name__ == "__main__":
    asyncio.run(main())
