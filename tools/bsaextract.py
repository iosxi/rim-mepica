"""Extract files from a Skyrim SE .bsa archive.

Used at build time only, to pull SkyUI's compiled scripts out of SkyUI_SE.bsa
so that pex2psc.py can reconstruct compiler stubs from them. Nothing extracted
here ends up in the distributed mod.

Usage: python bsaextract.py <archive.bsa> <substring filter> <output dir>
"""
import os
import struct
import sys
import zlib

SEP = chr(92)                       # archives store paths with backslashes

FLAG_DIR_NAMES = 0x1
FLAG_FILE_NAMES = 0x2
FLAG_COMPRESSED = 0x4
FLAG_EMBED_NAMES = 0x100


def read_index(fh):
    if fh.read(4) != b'BSA' + bytes([0]):
        raise SystemExit('not a BSA archive')
    (version, folder_offset, archive_flags, folder_count, file_count,
     _folder_name_len, file_name_len, _file_flags) = struct.unpack(
        '<8I', fh.read(32))

    fh.seek(folder_offset)
    folders = []
    for _ in range(folder_count):
        if version >= 105:
            _hash, count, _pad, offset = struct.unpack('<QIIQ', fh.read(24))
        else:
            _hash, count, offset = struct.unpack('<QII', fh.read(16))
        folders.append({'count': count, 'offset': offset, 'name': '',
                        'files': []})

    for folder in folders:
        # Folder record offsets are stored with the file-name block added in.
        fh.seek(folder['offset'] - file_name_len)
        if archive_flags & FLAG_DIR_NAMES:
            n = struct.unpack('<B', fh.read(1))[0]
            folder['name'] = fh.read(n).rstrip(bytes([0])).decode('cp1252')
        for _ in range(folder['count']):
            _hash, size, offset = struct.unpack('<QII', fh.read(16))
            folder['files'].append({'size': size, 'offset': offset, 'name': ''})

    if archive_flags & FLAG_FILE_NAMES:
        names = fh.read(file_name_len).split(bytes([0]))
        i = 0
        for folder in folders:
            for entry in folder['files']:
                entry['name'] = names[i].decode('cp1252')
                i += 1
    return folders, archive_flags


def decompress(raw):
    try:
        return zlib.decompress(raw)
    except zlib.error:
        import lz4.frame                 # Skyrim SE archives use LZ4 frames
        return lz4.frame.decompress(raw)


def extract(archive, needle, outdir):
    with open(archive, 'rb') as fh:
        folders, archive_flags = read_index(fh)
        written = 0
        for folder in folders:
            for entry in folder['files']:
                path = folder['name'] + SEP + entry['name']
                if needle and needle.lower() not in path.lower():
                    continue
                fh.seek(entry['offset'])
                size = entry['size']
                compressed = bool(archive_flags & FLAG_COMPRESSED)
                if size & 0x40000000:          # per-file inversion of the flag
                    compressed = not compressed
                    size &= ~0x40000000
                data = fh.read(size)
                if archive_flags & FLAG_EMBED_NAMES:
                    n = data[0]
                    data = data[1 + n:]
                if compressed:
                    data = decompress(data[4:])
                dest = os.path.join(outdir, path.replace(SEP, '/').lstrip('/'))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, 'wb') as out:
                    out.write(data)
                print('extracted', path, len(data))
                written += 1
        return written


if __name__ == '__main__':
    count = extract(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '',
                    sys.argv[3])
    if not count:
        raise SystemExit('nothing matched')
