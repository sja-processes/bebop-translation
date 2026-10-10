#!/usr/bin/env python3
"""Build script/en/NAME.txt from a translation draft.

usage: python3 tools/enbuild.py msg_XXX DRAFT.txt   (run from repo root)
Draft = "@@ ID" lines, each followed by the English text (codes kept).
Labels and trailing newlines are copied from script/jp/. Then run
tools/encheck.py.
"""
import re, sys
sys.path.insert(0, 'tools')
from encheck import parse, width, TOK, MAX_W

PAGE = re.compile(r'(\[(?:page|page\+goto[^\]]*)\]\n?)')


def wrap_block(lines):
    """Greedy re-wrap of consecutive text lines (codes are zero-width)."""
    words = ' '.join(lines).split(' ')
    out, cur = [], ''
    for w in words:
        if not w:
            continue
        cand = w if not cur else cur + ' ' + w
        if cur and width(cand) > MAX_W:
            out.append(cur); cur = w
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


def rewrap(text):
    """Only touches runs of text lines where some line is too wide."""
    parts = PAGE.split(text)
    for i in range(0, len(parts), 2):
        lines = parts[i].split('\n')
        res, run = [], []
        def flush():
            if any(width(l) > MAX_W for l in run):
                res.extend(wrap_block(run))
            else:
                res.extend(run)
            run.clear()
        for l in lines:
            if TOK.sub('', l).strip():
                run.append(l)
            else:
                flush(); res.append(l)
        flush()
        parts[i] = '\n'.join(res)
    return ''.join(parts)
name = sys.argv[1]
jp = parse('script/jp/%s.txt' % name, 'JP')
draft = open(sys.argv[2], encoding='utf-8').read()
out = ['# Be-Bop High School - English script, %s.\n# Translation only (no ROM text). Check with tools/encheck.py.\n\n' % name]
for chunk in re.split(r'^(?=@@ )', draft, flags=re.M)[1:]:
    head, body = chunk.split('\n', 1)
    mid = int(head.split()[1], 16)
    label, jt = jp[mid]
    trail = len(jt) - len(jt.rstrip('\n'))
    text = rewrap(body.rstrip('\n')) + '\n' * trail
    out.append('%s\nEN:\n%s\n\n' % (label, text))
open('script/en/%s.txt' % name, 'w', encoding='utf-8').write(''.join(out))
