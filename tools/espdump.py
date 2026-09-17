"""Dump and validate a Skyrim plugin file.

Written to check rim-mepica.esp against real MCM plugins. The VMAD parser is the
important part: it must consume the subrecord exactly, which is what proves the
quest/alias script layout is right.

Usage: python espdump.py <plugin.esp> [RECORDTYPE]
"""
import struct
import sys
import zlib

COMPRESSED = 0x00040000


def subrecords(data):
    i = 0
    pending_size = None
    while i + 6 <= len(data):
        tag = data[i:i + 4].decode('ascii', 'replace')
        size = struct.unpack_from('<H', data, i + 4)[0]
        i += 6
        if tag == 'XXXX':                     # oversized field marker
            pending_size = struct.unpack_from('<I', data, i)[0]
            i += size
            continue
        if pending_size is not None:
            size = pending_size
            pending_size = None
        yield tag, data[i:i + size]
        i += size


def walk(buf, off, end, depth, visit):
    while off < end:
        tag = buf[off:off + 4].decode('ascii', 'replace')
        size = struct.unpack_from('<I', buf, off + 4)[0]
        if tag == 'GRUP':
            label = buf[off + 8:off + 12]
            group_type = struct.unpack_from('<i', buf, off + 12)[0]
            visit('GRUP', label, group_type, depth, None, None)
            walk(buf, off + 24, off + size, depth + 1, visit)
            off += size
        else:
            flags = struct.unpack_from('<I', buf, off + 8)[0]
            formid = struct.unpack_from('<I', buf, off + 12)[0]
            data = buf[off + 24:off + 24 + size]
            if flags & COMPRESSED:
                data = zlib.decompress(data[4:])
            visit('REC', tag, flags, depth, formid, data)
            off += 24 + size


class VmadReader(object):
    def __init__(self, data):
        self.d = data
        self.i = 0

    def u8(self):
        v = self.d[self.i]
        self.i += 1
        return v

    def u16(self):
        v = struct.unpack_from('<H', self.d, self.i)[0]
        self.i += 2
        return v

    def i16(self):
        v = struct.unpack_from('<h', self.d, self.i)[0]
        self.i += 2
        return v

    def u32(self):
        v = struct.unpack_from('<I', self.d, self.i)[0]
        self.i += 4
        return v

    def f32(self):
        v = struct.unpack_from('<f', self.d, self.i)[0]
        self.i += 4
        return v

    def text(self):
        n = self.u16()
        v = self.d[self.i:self.i + n].decode('cp1252')
        self.i += n
        return v


def read_scripts(r, version, obj_format, indent, out):
    for _ in range(r.u16()):
        name = r.text()
        status = r.u8() if version >= 4 else 0
        count = r.u16()
        out.append('%sscript %r status=%d properties=%d'
                   % (indent, name, status, count))
        for _ in range(count):
            pname = r.text()
            ptype = r.u8()
            pstatus = r.u8() if version >= 4 else 0
            value = read_property(r, ptype, obj_format)
            out.append('%s  property %r type=%d status=%d value=%r'
                       % (indent, pname, ptype, pstatus, value))


def read_property(r, ptype, obj_format):
    if ptype == 1:
        if obj_format == 1:
            formid = r.u32()
            alias = r.i16()
            r.u16()
        else:
            r.u16()
            alias = r.i16()
            formid = r.u32()
        return 'form=%08X alias=%d' % (formid, alias)
    if ptype == 2:
        return r.text()
    if ptype == 3:
        return struct.unpack('<i', struct.pack('<I', r.u32()))[0]
    if ptype == 4:
        return r.f32()
    if ptype == 5:
        return bool(r.u8())
    if 11 <= ptype <= 15:
        return [read_property(r, ptype - 10, obj_format)
                for _ in range(r.u32())]
    raise ValueError('unknown VMAD property type %d' % ptype)


def parse_quest_vmad(data):
    """Parse a QUST VMAD. Raises unless it consumes the field exactly."""
    r = VmadReader(data)
    out = []
    version = r.i16()
    obj_format = r.i16()
    out.append('VMAD version=%d objectFormat=%d' % (version, obj_format))
    read_scripts(r, version, obj_format, '  ', out)

    out.append('  fragmentSectionVersion=%d' % r.u8())
    fragment_count = r.u16()
    out.append('  fragments=%d file=%r' % (fragment_count, r.text()))
    for _ in range(fragment_count):
        r.u16()
        r.i16()
        r.u32()
        r.text()
        r.text()

    alias_count = r.u16()
    out.append('  aliases=%d' % alias_count)
    for _ in range(alias_count):
        r.u16()
        alias = r.i16()
        formid = r.u32()
        aversion = r.i16()
        aformat = r.i16()
        out.append('    alias index=%d owner=%08X version=%d objectFormat=%d'
                   % (alias, formid, aversion, aformat))
        read_scripts(r, aversion, aformat, '      ', out)

    if r.i != len(data):
        raise ValueError('VMAD parse consumed %d of %d bytes' % (r.i, len(data)))
    out.append('  (consumed %d/%d bytes exactly)' % (r.i, len(data)))
    return out


def dump(path, only=None):
    buf = open(path, 'rb').read()

    def visit(kind, a, b, depth, formid, data):
        pad = '  ' * depth
        if kind == 'GRUP':
            print('%sGRUP %s type=%d' % (pad, a.decode('ascii', 'replace'), b))
            return
        if only and a != only:
            return
        print('%sREC %s flags=%08X formid=%08X size=%d'
              % (pad, a, b, formid, len(data)))
        for tag, sub in data and subrecords(data) or []:
            if tag == 'VMAD' and a == 'QUST':
                for line in parse_quest_vmad(sub):
                    print(pad + '   ' + line)
            else:
                shown = sub if len(sub) <= 48 else sub[:48] + b'...'
                print('%s   %s [%d] %r' % (pad, tag, len(sub), shown))

    size = struct.unpack_from('<I', buf, 4)[0]
    visit('REC', buf[0:4].decode(), struct.unpack_from('<I', buf, 8)[0], 0,
          struct.unpack_from('<I', buf, 12)[0], buf[24:24 + size])
    walk(buf, 24 + size, len(buf), 0, visit)


if __name__ == '__main__':
    dump(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
