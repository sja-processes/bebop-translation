#!/usr/bin/env python3
"""Build a release BPS from a git tag (Stephen, 2026-11-05).

usage: tools/release.py            build the release for the tag on HEAD
       tools/release.py --notes    also print the GitHub release command

1. Tag the commit to release:  git tag -a v1.0 -m "Version 1.0"
2. Run this. It refuses an untracked/uncommitted tree or a HEAD without
   a v* tag, then builds with the tag's version ("1.0") and the tagged
   commit's date ("2026.11") baked into the title screen's Left/Right
   info, so the same tag always gives the same patch.
3. It writes out/release/bebop_en-v1.0.bps and RELEASE-v1.0.md (notes:
   the ROM to patch, the patched ROM's MD5/SHA-1/CRC32, emulator
   settings, the changes list from PLAN.md),
   and checks that Flips (~/Downloads/flips/flips-linux, or $FLIPS)
   applies the patch to exactly the ROM we built.

Publishing is separate and only on Stephen's say-so (it pushes): push the
commit and tag, then `gh release create v1.0 out/release/bebop_en-v1.0.bps
--title "..." --notes-file out/release/RELEASE-v1.0.md`. The build needs
the Japanese ROM, which must never be uploaded anywhere, so releases are
built here, not by GitHub Actions.
"""
import hashlib
import zlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import insert  # noqa: E402

TITLE = 'Be-Bop-Highschool: English translation'
# Stephen's Flips (the patcher players use); FLIPS=... overrides
FLIPS = os.environ.get('FLIPS', os.path.expanduser('~/Downloads/flips/flips-linux'))


def check_with_flips(bps_path, old, new):
    """Apply the patch with Flips too: it must give exactly our ROM."""
    flips = shutil.which(FLIPS) or (FLIPS if os.access(FLIPS, os.X_OK) else None)
    if not flips:
        sys.exit('Flips not found at %s (set FLIPS=/path/to/flips)' % FLIPS)
    with tempfile.TemporaryDirectory() as d:
        src, out = os.path.join(d, 'original.nes'), os.path.join(d, 'patched.nes')
        open(src, 'wb').write(old)
        r = subprocess.run([flips, '--apply', bps_path, src, out], capture_output=True, text=True)
        if r.returncode or not os.path.exists(out) or open(out, 'rb').read() != new:
            sys.exit('Flips gave a different ROM: %s%s' % (r.stdout, r.stderr))


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def tag_on_head():
    try:
        tag = git('describe', '--tags', '--exact-match', '--match', 'v*', 'HEAD')
    except subprocess.CalledProcessError:
        sys.exit('HEAD has no v* tag: git tag -a v1.0 -m "Version 1.0" first')
    if not re.fullmatch(r'v\d+(\.\d+)*', tag):
        sys.exit('tag %r is not like v1.0' % tag)
    return tag


def plan_section(name):
    text = open(os.path.join(ROOT, 'PLAN.md'), encoding='utf-8').read()
    m = re.search(r'^### %s[^\n]*\n(.*?)(?=^### )' % re.escape(name), text, re.S | re.M)
    return m.group(1).strip() if m else ''


def hashes(data):
    """-> (MD5, SHA-1, CRC32) of a ROM file, as lower-case hex."""
    return (hashlib.md5(data).hexdigest(), hashlib.sha1(data).hexdigest(),
            '%08x' % zlib.crc32(data))


def notes(tag, date, rom_sha1, bps_name, patched):
    return '\n'.join([
        '# %s, %s' % (TITLE, tag), '',
        'Built %s from commit %s.' % (date, git('rev-parse', '--short=7', 'HEAD')), '',
        '## How to apply', '',
        'Apply `%s` (BPS, e.g. with Flips or Rom Patcher JS) to the original Japanese' % bps_name,
        'ROM *Be-Bop-Highschool - Koukousei Gokuraku Densetsu (Japan).nes*,',
        'SHA-1 `%s`. The ROM is not included.' % rom_sha1.upper(), '',
        'The patched ROM (with its 16-byte iNES header, like the original) should be:', '',
        '| | |', '|---|---|',
        '| MD5 | `%s` |' % patched[0],
        '| SHA-1 | `%s` |' % patched[1],
        '| CRC32 | `%s` |' % patched[2], '',
        'On the title screen, press Left or Right to show the version.', '',
        '## Notes', '', '\n'.join(l for l in plan_section('Release notes').splitlines()
                                  if 'SHA-1 above' not in l), '',
        '## Changes beyond the translation', '', plan_section('Quality-of-life changes'), '',
    ])


def main():
    if git('status', '--porcelain'):
        sys.exit('uncommitted changes: commit or stash them first')
    tag = tag_on_head()
    version = tag[1:]
    y, m, _ = git('log', '-1', '--format=%cs', 'HEAD').split('-')
    date = '%s.%s' % (y, m)
    old, new, *_ = insert.build(version, date)
    bpatch = insert.bps(old, new)
    assert insert.apply_bps(old, bpatch) == new
    insert.check_no_rom_data(old, bpatch)
    outdir = os.path.join(ROOT, 'out', 'release')
    os.makedirs(outdir, exist_ok=True)
    bps_name = 'bebop_en-%s.bps' % tag
    open(os.path.join(outdir, bps_name), 'wb').write(bpatch)
    check_with_flips(os.path.join(outdir, bps_name), old, new)
    note_name = 'RELEASE-%s.md' % tag
    open(os.path.join(outdir, note_name), 'w', encoding='utf-8').write(
        notes(tag, '%s-%s' % (y, m), hashlib.sha1(old).hexdigest(), bps_name, hashes(new)))
    print('built %s (%d bytes): title shows "%s" / "%s"'
          % (bps_name, len(bpatch), *insert.titleinfo.version_info(version, date)))
    print('Flips applies it to the identical ROM')
    print('notes: out/release/%s' % note_name)
    if '--notes' in sys.argv:
        print('\nTo publish (pushes; only when Stephen says):')
        print('  git push origin main %s' % tag)
        print('  gh release create %s out/release/%s --title "%s %s" --notes-file out/release/%s'
              % (tag, bps_name, TITLE, tag, note_name))


if __name__ == '__main__':
    main()
