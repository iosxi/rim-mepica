"""Generate compile-time .psc stubs from compiled .pex files.

The Papyrus compiler needs source for every ancestor script. SkyUI ships only
compiled scripts, so we reconstruct the declarations (names, types, signatures)
straight from the shipped .pex. Bodies are empty: the stubs exist purely to
satisfy the compiler and are never distributed. At runtime the real SkyUI
scripts are the ones that load.
"""
import os
import struct
import sys

OPARGS = {0x00: 0, 0x01: 3, 0x02: 3, 0x03: 3, 0x04: 3, 0x05: 3, 0x06: 3,
          0x07: 3, 0x08: 3, 0x09: 3, 0x0A: 2, 0x0B: 2, 0x0C: 2, 0x0D: 2,
          0x0E: 2, 0x0F: 3, 0x10: 3, 0x11: 3, 0x12: 3, 0x13: 3, 0x14: 1,
          0x15: 2, 0x16: 2, 0x17: 3, 0x18: 2, 0x19: 3, 0x1A: 1, 0x1B: 3,
          0x1C: 3, 0x1D: 3, 0x1E: 2, 0x1F: 2, 0x20: 3, 0x21: 3, 0x22: 4,
          0x23: 4}
VARARG = (0x17, 0x18, 0x19)

# Provided by ScriptObject; redeclaring them breaks the compile.
SKIP = {'getstate', 'gotostate', 'onbeginstate', 'onendstate'}

DEFAULT_RETURN = {'bool': 'false', 'int': '0', 'float': '0.0', 'string': '""'}


class Reader(object):
    def __init__(self, data):
        self.d = data
        self.i = 0

    def u8(self):
        v = self.d[self.i]
        self.i += 1
        return v

    def u16(self):
        v = struct.unpack_from('>H', self.d, self.i)[0]
        self.i += 2
        return v

    def u32(self):
        v = struct.unpack_from('>I', self.d, self.i)[0]
        self.i += 4
        return v

    def u64(self):
        v = struct.unpack_from('>Q', self.d, self.i)[0]
        self.i += 8
        return v

    def f32(self):
        v = struct.unpack_from('>f', self.d, self.i)[0]
        self.i += 4
        return v

    def wstring(self):
        n = self.u16()
        v = self.d[self.i:self.i + n].decode('cp1252')
        self.i += n
        return v


def parse(path):
    r = Reader(open(path, 'rb').read())
    if r.u32() != 0xFA57C0DE:
        raise SystemExit('not a Skyrim .pex: ' + path)
    r.u8()
    r.u8()
    r.u16()
    r.u64()
    r.wstring()
    r.wstring()
    r.wstring()
    strings = [r.wstring() for _ in range(r.u16())]

    if r.u8():                                        # optional debug info
        r.u64()
        for _ in range(r.u16()):
            r.u16()
            r.u16()
            r.u16()
            r.u8()
            for _ in range(r.u16()):
                r.u16()

    flagnames = {}
    for _ in range(r.u16()):
        name = strings[r.u16()]
        flagnames[r.u8()] = name

    def flags_of(value):
        return [n for bit, n in flagnames.items() if value & (1 << bit)]

    def vardata():
        t = r.u8()
        if t == 0:
            return None
        if t in (1, 2):
            return strings[r.u16()]
        if t == 3:
            return struct.unpack('>i', struct.pack('>I', r.u32()))[0]
        if t == 4:
            return r.f32()
        if t == 5:
            return bool(r.u8())
        raise SystemExit('unknown VariableData type %d' % t)

    def function():
        rettype = strings[r.u16()]
        r.u16()
        userflags = r.u32()
        fl = r.u8()
        params = []
        for _ in range(r.u16()):
            pname = strings[r.u16()]
            ptype = strings[r.u16()]
            params.append((ptype, pname))
        for _ in range(r.u16()):                      # locals
            r.u16()
            r.u16()
        for _ in range(r.u16()):                      # instructions
            op = r.u8()
            for _ in range(OPARGS[op]):
                vardata()
            if op in VARARG:
                for _ in range(vardata()):
                    vardata()
        return rettype, params, bool(fl & 1), bool(fl & 2), flags_of(userflags)

    objects = []
    for _ in range(r.u16()):
        name = strings[r.u16()]
        size = r.u32()
        end = r.i + size - 4
        parent = strings[r.u16()]
        r.u16()
        userflags = r.u32()
        strings[r.u16()]                              # auto state name
        obj = {'name': name, 'parent': parent, 'flags': flags_of(userflags),
               'props': [], 'funcs': []}
        for _ in range(r.u16()):                      # variables stay private
            r.u16()
            r.u16()
            r.u32()
            vardata()
        for _ in range(r.u16()):
            pname = strings[r.u16()]
            ptype = strings[r.u16()]
            r.u16()
            pflags = r.u32()
            fl = r.u8()
            auto = bool(fl & 4)
            if auto:
                r.u16()
            else:
                if fl & 1:
                    function()
                if fl & 2:
                    function()
            obj['props'].append((ptype, pname, auto, bool(fl & 1),
                                 bool(fl & 2), flags_of(pflags)))
        for _ in range(r.u16()):                      # states
            r.u16()
            for _ in range(r.u16()):
                fname = strings[r.u16()]
                obj['funcs'].append((fname,) + function())
        r.i = end
        objects.append(obj)
    return objects


def emit(obj):
    out = []
    head = 'Scriptname ' + obj['name']
    if obj['parent']:
        head += ' extends ' + obj['parent']
    for f in obj['flags']:
        head += ' ' + f
    out.append(head)
    out.append('{Compile-time stub generated from ' + obj['name'] +
               '.pex - not shipped with the mod.}')
    out.append('')

    for ptype, pname, auto, has_get, has_set, pflags in obj['props']:
        suffix = ''.join(' ' + f for f in pflags)
        if not auto and has_get and not has_set:
            out.append('%s Property %s%s' % (ptype, pname, suffix))
            out.append('    %s Function Get()' % ptype)
            out.append('        return %s'
                       % DEFAULT_RETURN.get(ptype.lower(), 'none'))
            out.append('    EndFunction')
            out.append('EndProperty')
        else:
            out.append('%s Property %s Auto%s' % (ptype, pname, suffix))
    out.append('')

    for name, rettype, params, is_global, is_native, userflags in obj['funcs']:
        if name.lower() in SKIP:
            continue
        sig = ', '.join('%s %s' % (t, n) for t, n in params)
        void = rettype.lower() in ('none', '')
        is_event = void and name.lower().startswith('on')
        mods = ''
        if is_global:
            mods += ' Global'
        if is_native:
            mods += ' Native'
        for f in userflags:
            mods += ' ' + f
        if is_event:
            out.append('Event %s(%s)%s' % (name, sig, mods))
            if not is_native:
                out.append('EndEvent')
        else:
            if void:
                decl = 'Function %s(%s)' % (name, sig)
            else:
                decl = '%s Function %s(%s)' % (rettype, name, sig)
            out.append(decl + mods)
            if not is_native:
                if not void:
                    out.append('    return %s'
                               % DEFAULT_RETURN.get(rettype.lower(), 'none'))
                out.append('EndFunction')
        out.append('')
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    for src in sys.argv[2:]:
        for obj in parse(src):
            dest = os.path.join(outdir, obj['name'] + '.psc')
            with open(dest, 'w', encoding='cp1252') as fh:
                fh.write(emit(obj))
            print('wrote', dest)
