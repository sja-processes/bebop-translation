#!/usr/bin/env python3
"""Build script/en/NAME.txt from a translation draft.

usage: python3 tools/enbuild.py msg_XXX DRAFT.txt   (run from repo root)
Draft = "@@ ID" lines, each followed by the English text (codes kept).
Labels and trailing newlines are copied from script/jp/. Then run
tools/encheck.py.
"""
import re, sys
sys.path.insert(0, 'tools')
from encheck import parse
name = sys.argv[1]
jp = parse('script/jp/%s.txt' % name, 'JP')
draft = open(sys.argv[2], encoding='utf-8').read()
out = ['# Be-Bop High School - English script, %s.\n# Translation only (no ROM text). Check with tools/encheck.py.\n\n' % name]
for chunk in re.split(r'^(?=@@ )', draft, flags=re.M)[1:]:
    head, body = chunk.split('\n', 1)
    mid = int(head.split()[1], 16)
    label, jt = jp[mid]
    trail = len(jt) - len(jt.rstrip('\n'))
    text = body.rstrip('\n') + '\n' * trail
    out.append('%s\nEN:\n%s\n\n' % (label, text))
open('script/en/%s.txt' % name, 'w', encoding='utf-8').write(''.join(out))
