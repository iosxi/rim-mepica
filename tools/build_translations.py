"""Convert the UTF-8 translation sources into the format Skyrim reads.

Skyrim wants Interface/Translations/<plugin name>_<language>.txt as UTF-16 LE
with a BOM and CRLF line endings, one "$key<tab>text" pair per line. Keeping the
sources as plain UTF-8 makes them readable and diffable; this step does the
conversion.

Usage: python build_translations.py <source dir> <output dir> <plugin base name>
"""
import os
import sys


def convert(src, dest):
    with open(src, encoding='utf-8') as fh:
        lines = [line.rstrip('\n').rstrip('\r') for line in fh]
    lines = [line for line in lines if line.strip()]
    for line in lines:
        if not line.startswith('$') or '\t' not in line:
            raise SystemExit('bad translation line in %s: %r' % (src, line))
    body = '\r\n'.join(lines) + '\r\n'
    with open(dest, 'wb') as fh:
        fh.write(b'\xff\xfe')                     # UTF-16 LE byte order mark
        fh.write(body.encode('utf-16-le'))
    return len(lines)


if __name__ == '__main__':
    srcdir, outdir, base = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    for name in sorted(os.listdir(srcdir)):
        if not name.endswith('.txt'):
            continue
        language = os.path.splitext(name)[0]
        dest = os.path.join(outdir, '%s_%s.txt' % (base, language))
        count = convert(os.path.join(srcdir, name), dest)
        print('wrote %s (%d entries)' % (dest, count))
