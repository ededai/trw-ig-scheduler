#!/usr/bin/env python3
"""
Ed's house rules for the copy gate. OURS, not upstream.

`copy_scan.py` is vendored third-party code from NulightJens/humanizer-stack
(commit 13f5c02) and must stay byte-identical to upstream so future updates
diff cleanly. Every TRW/AURA-specific rule lives HERE instead.

Usage:

    import copy_scan, house_rules
    rules = house_rules.extend(copy_scan.compile_rules())
    hits  = copy_scan.scan(text, rules, path)

Rule schema matches copy_scan.RULES exactly: id, label, fix, pats, and an
optional suppress regex. House rule ids are prefixed `house-` so provenance
is obvious in any gate output.

Added 2026-08-19. See ~/.claude/skills/structural-humanizer/references/local-additions.md
"""

import re

# Lines that are code, markup, or quoted material are not user-facing copy.
CODE_SUPPRESS = r"^\s*(\*|//|/\*|<!--|#|>|\||```)|`[^`]*`"

HOUSE_RULES = [
    {
        "id": "house-zero-dash",
        "label": "Em dash or en dash. Ed's standing rule is zero, always, no exceptions.",
        "fix": "Use a comma, a period, or parentheses. Year ranges take a hyphen: 2013-2018.",
        "pats": [r"[—–]", r"&mdash;", r"&ndash;"],
        "suppress": CODE_SUPPRESS,
    },
    {
        # Widens upstream's copy-antithesis, which only fires on the contracted
        # form ("it's"). Verified 2026-08-19: upstream missed 4 of 6 realistic
        # TRW phrasings, including "not just high, it is the highest since 2023".
        "id": "house-antithesis",
        "label": 'The "not just X, it is Y" sentence (the AI accent, spelled-out forms)',
        "fix": "State the thing plainly. Lead with the real claim and drop the negation.",
        "pats": [
            r"(it'?s |it |that'?s |that |this |they'?re |they )?\bnot just\b"
            r"[^.,;!?]{1,40},?\s*"
            r"(it'?s|it is|that'?s|that is|this is|they'?re|they are|we|but)\b",
            r"\bnot only\b[^.,;!?]{1,40},?\s*but\b",
            r"\bisn'?t (just|only)\b[^.,;!?]{1,40},?\s*(it'?s|it is|but)\b",
        ],
        "suppress": CODE_SUPPRESS,
    },
]


def compile_house():
    """Compile house rules into copy_scan's runtime shape."""
    out = []
    for r in HOUSE_RULES:
        out.append({
            **r,
            "re": [re.compile(p, re.I) for p in r["pats"]],
            "suppress_re": re.compile(r["suppress"], re.I) if r.get("suppress") else None,
        })
    return out


def extend(vendored_rules):
    """Append house rules to compiled upstream rules. Upstream is never mutated."""
    return list(vendored_rules) + compile_house()
