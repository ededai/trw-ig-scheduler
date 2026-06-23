#!/usr/bin/env python3
"""TRW site-search — single source of truth for the search component.

This module owns the search bar HTML+JS and the keyword logic for the
`window.TRW_SEARCH_CORPUS` typeahead used on /blog/, /topics/, every
/topics/{tag}/ archive, and /news/.

Why this file exists: before 2026-06-23 the search JS was DUPLICATED inline
in wp-import/push_blog_hub.py and wp-import/push_tag_pages.py, and the corpus
held only {n: title, u: url}. The matcher did a literal substring match on the
title, so the placeholder advertised terms ("brakes", "tyres", "warranty",
"monsoon", "first service") that all returned zero results. Two fixes live here:

  1. rank() tokenises the query and matches across title + keywords ('k'),
     ranking title hits above keyword hits.
  2. Enter navigates to the top result (not only when there is exactly one).

Keywords for each post come from its topic_tags.json tags (auto — a new post
needs nothing) plus optional synonym overrides in search_keyword_overrides.json.

CANONICAL COPY: trw-ig-scheduler/blog/trw_search.py (this file — used by the
daily cron's refresh_search_corpus.py). A mirror lives at wp-import/trw_search.py
for the local one-shot generators. Keep them identical.
"""
from __future__ import annotations
import json, html, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OVERRIDES_PATH = HERE / "search_keyword_overrides.json"


# ── keyword logic ──────────────────────────────────────────────────────────

def load_keyword_overrides(path: Path | None = None) -> dict:
    """slug -> synonym string. Keys starting with '_' are metadata, skipped."""
    p = path or OVERRIDES_PATH
    try:
        raw = json.loads(p.read_text())
    except FileNotFoundError:
        return {}
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def keywords_for(slug: str, tags, overrides: dict | None = None) -> str:
    """Build the lowercase keyword string for a post.

    tags: list of tag slugs from topic_tags.json (e.g. ["brakes", "driving-tips"]).
    Combines: tag slugs + tags with hyphens as spaces + synonym overrides.
    Deduped, order-stable, single-space separated.
    """
    ov = load_keyword_overrides() if overrides is None else overrides
    parts: list[str] = []
    for t in (tags or []):
        t = str(t).strip().lower()
        if not t:
            continue
        parts.append(t)
        if "-" in t:
            parts.append(t.replace("-", " "))
    extra = ov.get(slug, "")
    if extra:
        parts.append(extra.lower())
    # tokenise, dedupe preserving order
    seen, out = set(), []
    for tok in " ".join(parts).split():
        if tok not in seen:
            seen.add(tok)
            out.append(tok)
    return " ".join(out)


def corpus_item(slug: str, title: str, tags, overrides: dict | None = None) -> dict:
    """One {n, u, k} corpus entry. title is the already-clean display title."""
    return {
        "n": html.unescape(re.sub(r"<[^>]+>", "", title)).strip(),
        "u": f"/{slug.strip('/')}/",
        "k": keywords_for(slug.strip('/'), tags, overrides),
    }


# ── search bar HTML + JS (the ONE canonical implementation) ────────────────

def build_search_bar(corpus, scope, chip_label):
    """Render the TRW search bar HTML+JS with a baked-in corpus.

    corpus: list of {"n": name, "u": url, "k": keywords}.
    scope: 'blog' | 'tags' | 'tag-archive'.
    chip_label: text for the left scope chip (e.g. 'All Posts', 'In Aircon').
    The CSS lives in each page's <style> block already.
    """
    corpus_json = json.dumps(corpus, ensure_ascii=False)
    chip_html = html.escape(chip_label)
    return (
        '<section class="trw-search-section">'
          '<div class="wrapper">'
            f'<div class="trw-search" data-scope="{scope}" role="search">'
              '<div class="trw-search-field">'
                f'<span class="trw-search-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.59 13.41 13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>{chip_html}</span>'
                '<input class="trw-search-input" type="search" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" aria-label="Search" aria-expanded="false" aria-haspopup="listbox" />'
                '<svg class="trw-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>'
                '<button type="button" class="trw-search-clear" aria-label="Clear search">&times;</button>'
              '</div>'
              '<div class="trw-search-dropdown" role="listbox" aria-label="Search suggestions"></div>'
            '</div>'
          '</div>'
        '</section>'
        f'<script>window.TRW_SEARCH_CORPUS={corpus_json};</script>'
        '<script>(function(){'
          'var root=document.querySelector(".trw-search");'
          'if(!root||!window.TRW_SEARCH_CORPUS)return;'
          'var field=root.querySelector(".trw-search-field"),chip=root.querySelector(".trw-search-chip");'
          'if(chip&&!chip.querySelector("svg")){var dc=document.createElement("div");dc.innerHTML=\'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.59 13.41 13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>\';chip.insertBefore(dc.firstChild,chip.firstChild);}'
          'if(field&&!field.querySelector(".trw-search-input")){var df=document.createElement("div");df.innerHTML=\'<input class="trw-search-input" type="search" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" aria-label="Search" aria-expanded="false" aria-haspopup="listbox"><svg class="trw-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>\';var beforeNode=field.querySelector(".trw-search-clear")||null;while(df.firstChild){field.insertBefore(df.firstChild,beforeNode);}}'
          'var input=root.querySelector(".trw-search-input"),dropdown=root.querySelector(".trw-search-dropdown"),clearBtn=root.querySelector(".trw-search-clear"),corpus=window.TRW_SEARCH_CORPUS,scope=root.getAttribute("data-scope")||"blog";'
          'var phs={"blog":["Try \\"aircon\\"","Try \\"brakes\\"","Try \\"COE\\"","Try \\"first service\\"","Search blog posts"],"tags":["Try \\"aircon\\"","Try \\"monsoon\\"","Try \\"warranty\\"","Try \\"tyres\\"","Search topics"],"tag-archive":["Search posts in this topic","Try a keyword","Search this topic"]};'
          'var labels=phs[scope]||phs["blog"],phIdx=0;'
          'function rotatePh(){if(document.activeElement===input||input.value)return;input.setAttribute("placeholder",labels[phIdx%labels.length]+"\\u2026");phIdx++}'
          'rotatePh();var phTimer=setInterval(rotatePh,2800);'
          'function escHtml(s){return s.replace(/[&<>"\']/g,function(c){return ({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","\'":"&#39;"})[c]})}'
          'function escReg(s){return s.replace(/[.*+?^${}()|[\\]\\\\]/g,"\\\\$&")}'
          'function rank(q){q=q.trim().toLowerCase();if(!q)return [];var toks=q.split(/\\s+/);var t0=[],t1=[],t2=[];for(var i=0;i<corpus.length;i++){var it=corpus[i],n=(it.n||"").toLowerCase();if(!n)continue;var hay=n+" "+((it.k||"").toLowerCase());var inTitle=true,inHay=true;for(var x=0;x<toks.length;x++){var tk=toks[x];if(!tk)continue;if(n.indexOf(tk)<0)inTitle=false;if(hay.indexOf(tk)<0)inHay=false}if(!inHay)continue;if(n.indexOf(q)===0)t0.push(it);else if(inTitle)t1.push(it);else t2.push(it)}function bn(a,b){return a.n.localeCompare(b.n)}t0.sort(bn);t1.sort(bn);t2.sort(bn);return t0.concat(t1).concat(t2)}'
          'function highlight(name,q){if(!q)return escHtml(name);var rgx=new RegExp("("+escReg(q)+")","ig");return escHtml(name).replace(rgx,"<mark>$1</mark>")}'
          'var activeIdx=-1;'
          'function render(q){var results=rank(q);activeIdx=-1;if(!q.trim()){close();return}if(!results.length){dropdown.innerHTML=\'<div class="trw-search-empty">No matches. <a href="/blog/">Browse all posts &rarr;</a></div>\';open();return}var html="";for(var i=0;i<results.length;i++){var r=results[i];html+=\'<a class="trw-search-item" role="option" href="\'+r.u+\'" data-idx="\'+i+\'"><span class="trw-search-item-name">\'+highlight(r.n,q.trim())+\'</span><span class="trw-search-item-arrow">&rarr;</span></a>\'}dropdown.innerHTML=html;open()}'
          'function open(){root.classList.add("is-open");input.setAttribute("aria-expanded","true")}'
          'function close(){root.classList.remove("is-open");input.setAttribute("aria-expanded","false");activeIdx=-1}'
          'function setActive(i){var items=dropdown.querySelectorAll(".trw-search-item");if(!items.length)return;if(i<0)i=items.length-1;if(i>=items.length)i=0;activeIdx=i;for(var j=0;j<items.length;j++)items[j].classList.toggle("is-active",j===i);items[i].scrollIntoView({block:"nearest"})}'
          'input.addEventListener("input",function(){var v=input.value;root.classList.toggle("has-value",!!v);render(v)});'
          'input.addEventListener("focus",function(){clearInterval(phTimer);if(input.value)render(input.value)});'
          'input.addEventListener("blur",function(){setTimeout(function(){if(!root.contains(document.activeElement))close()},150)});'
          'input.addEventListener("keydown",function(e){var items=dropdown.querySelectorAll(".trw-search-item");if(e.key==="ArrowDown"){e.preventDefault();if(items.length)setActive(activeIdx+1)}else if(e.key==="ArrowUp"){e.preventDefault();if(items.length)setActive(activeIdx-1)}else if(e.key==="Enter"){if(activeIdx>=0&&items[activeIdx]){e.preventDefault();window.location.href=items[activeIdx].getAttribute("href")}else if(items.length){e.preventDefault();window.location.href=items[0].getAttribute("href")}}else if(e.key==="Escape"){close();input.blur()}});'
          'clearBtn.addEventListener("click",function(){input.value="";root.classList.remove("has-value");close();input.focus()});'
          'document.addEventListener("click",function(e){if(!root.contains(e.target))close()});'
        '})();</script>'
    )


# Regex that matches an existing rendered search block on a live page
# (section + corpus script + init script), so refresh_search_corpus.py can
# swap the whole block atomically. Non-greedy, DOTALL.
SEARCH_BLOCK_RE = re.compile(
    r'<section class="trw-search-section">.*?</section>'
    r'\s*<script>window\.TRW_SEARCH_CORPUS=.*?</script>'
    r'\s*<script>\(function\(\)\{.*?\}\)\(\);</script>',
    re.S,
)
