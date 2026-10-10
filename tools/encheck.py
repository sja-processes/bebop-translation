#!/usr/bin/env python3
"""Check English script files against the Japanese dump.

usage: tools/encheck.py [script/en/msg_XXX.txt ...]   (default: all)

For every message in an EN file, checks against script/jp/ that:
  - the ID exists and the label matches,
  - the sequence of [code ...] and <XX> tokens is identical,
  - trailing newlines match (they are real F5 bytes),
and warns (does not fail) on lines > 24 glyphs or pages > 4 lines.
Name codes count as their longest expansion (7: Hiroshi / Nakama).
"""
import re, sys, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK = re.compile(r'\[[^\]]*\]|<[0-9A-Fa-f]{2}>')
NAME_CODES = {'cmdE1', 'cmdE2', 'cmdDF', 'cmdE0'}
NAME_LEN = 7
MAX_W, MAX_L = 24, 4


def parse(path, block):
    """-> {id: (label, text)} for blocks named `block` (JP or EN)."""
    out = {}
    src = open(path, encoding='utf-8').read()
    for chunk in re.split(r'^(?=@@ )', src, flags=re.M)[1:]:
        label, body = chunk.split('\n', 1)
        mid = int(label.split()[1], 16)
        m = re.search(r'^%s:\n' % block, body, flags=re.M)
        if not m:
            continue
        text = body[m.end():]
        nxt = re.search(r'^(JP|EN):\n', text, flags=re.M)
        if nxt:
            text = text[:nxt.start()]
            assert text.endswith('\n'), (path, label)
            text = text[:-1]
        else:
            assert text.endswith('\n\n'), (path, label)
            text = text[:-2]
        out[mid] = (label, text)
    return out


def width(line):
    w = 0
    for part in re.split(r'(\[[^\]]*\]|<[0-9A-Fa-f]{2}>)', line):
        if part.startswith('['):
            if part[1:-1].split()[0] in NAME_CODES:
                w += NAME_LEN
        elif part.startswith('<'):
            w += 1
        else:
            w += len(part)
    return w


def check_file(path, jp):
    errs = warns = 0
    en = parse(path, 'EN')
    for mid, (label, text) in sorted(en.items()):
        if mid not in jp:
            print('%s %03X: no such message' % (path, mid)); errs += 1; continue
        jlabel, jtext = jp[mid]
        if label.split()[:3] != jlabel.split()[:3]:
            print('%03X: label mismatch' % mid); errs += 1
        if TOK.findall(text) != TOK.findall(jtext):
            print('%03X: codes differ\n  JP %s\n  EN %s' % (
                mid, TOK.findall(jtext), TOK.findall(text))); errs += 1
        tj = len(jtext) - len(jtext.rstrip('\n'))
        te = len(text) - len(text.rstrip('\n'))
        if tj != te:
            print('%03X: trailing newlines JP %d EN %d' % (mid, tj, te)); errs += 1
        if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', text):
            print('%03X: untranslated Japanese left' % mid); warns += 1
        for page in re.split(r'\[(?:page|page\+goto[^\]]*)\]\n?', text):
            lines = [l for l in page.split('\n') if TOK.sub('', l).strip()]
            if len(lines) > MAX_L:
                print('%03X: warn %d lines on a page' % (mid, len(lines))); warns += 1
            for l in lines:
                if width(l) > MAX_W:
                    print('%03X: warn width %d: %s' % (mid, width(l), l)); warns += 1
    return errs, warns, len(en)


def main():
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, 'script/en/*.txt')))
    te = tw = 0
    for f in files:
        jp = parse(os.path.join(ROOT, 'script/jp', os.path.basename(f)), 'JP')
        e, w, n = check_file(f, jp)
        print('%s: %d messages, %d errors, %d warnings (JP has %d)' % (
            os.path.relpath(f, ROOT), n, e, w, len(jp)))
        te += e; tw += w
    sys.exit(1 if te else 0)


if __name__ == '__main__':
    main()
