# Vendored Writing & SEO Skills (Bryan)

Snapshot of the 10-skill writing + SEO stack that Bryan's article + caption drafting code reads at LLM-prompt time. Vendored here so any cron run works without depending on `~/.claude/skills/` (which doesn't exist in GitHub Actions runners).

## Source of truth

The originals live on Ed's Mac:
- `~/.claude/skills/` — system Claude Code skills
- `~/Desktop/Claude folder/Skills/` — TRW marketing pack

This directory is a **read-only mirror**. To refresh, run:

```bash
./tools/sync_skills.sh
```

That script copies the latest version from the two source locations and prints a diff summary.

## The 10-skill stack

| # | Phase | Skill | Folder |
|---|---|---|---|
| 1 | Pre-draft | anti-ai-slop-writing | `anti-ai-slop-writing/` |
| 2 | Pre-draft | copywriting | `copywriting/` |
| 3 | Pre-draft | doc-coauthoring | `doc-coauthoring/` |
| 4 | During | claude-seo → seo-content | `claude-seo/agents/seo-content.md` |
| 5 | During | claude-seo → seo-google | `claude-seo/agents/seo-google.md` |
| 6 | During | claude-seo → seo-technical | `claude-seo/agents/seo-technical.md` |
| 7 | During | ai-seo | `ai-seo/` |
| 8 | During | schema-markup | `schema-markup/` |
| 9 | Post-draft | avoid-ai-writing | `avoid-ai-writing/` |
| 10 | Post-draft | copy-editing | `copy-editing/` |

## What was stripped

To keep the repo lean, the following were removed from the `claude-seo/` snapshot since they aren't needed at LLM-prompt time:
- `.git/`, `.github/`, `.devcontainer/`, `.claude-plugin/` — source-repo scaffolding (~2.3MB)
- `screenshots/` — visual docs (~2MB of PNGs)
- `scripts/` — Python runners for Bing/GA4/CommonCrawl APIs
- `extensions/` — DataForSEO / Firecrawl integrations
- Installer scripts and license/citation metadata

Prompt-content essentials preserved: `agents/`, `skills/`, `docs/`, `pdf/`, `schema/`, `hooks/`.

## Last sync

See `STAMP.txt` for the last successful sync timestamp.
