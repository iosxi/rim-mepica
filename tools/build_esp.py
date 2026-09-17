"""Build rim-mepica.esp.

The plugin holds exactly one thing: a start-game-enabled quest that carries the
MCM script, plus a PlayerRef alias so SkyUI's SKI_PlayerLoadGameAlias can tell
the quest when a save has been loaded.

The record layout mirrors what the Creation Kit writes for a minimal MCM
plugin; it was derived by decoding existing MCM plugins byte for byte
(see docs/format-notes.md).
"""
import os
import struct
import sys

PLUGIN_NAME = 'rim-mepica.esp'
AUTHOR = 'nekoryu'
DESCRIPTION = 'Periodically clear the undead eye glow stuck on the player.'
QUEST_EDID = b'rimmepica_MCMQuest'
QUEST_SCRIPT = b'rimmepica_MCM'
ALIAS_SCRIPT = b'SKI_PlayerLoadGameAlias'
MASTERS = [b'Skyrim.esm']

FORM_VERSION = 44                  # what Skyrim SE stamps on records
HEADER_VERSION = 1.70
ESL_FLAG = 0x00000200              # light plugin: no load order slot used
PLAYER_REF = 0x00000014            # Skyrim.esm, index 0 of our master list

# Light plugins must keep their object indices inside 0x800-0xFFF. The high
# byte equals the number of masters, which is how the engine says "this file".
QUEST_FORMID = (len(MASTERS) << 24) | 0x000800


def zstring(text):
    return text + bytes([0])


def subrecord(tag, data):
    return tag + struct.pack('<H', len(data)) + data


def record(tag, flags, formid, data):
    header = struct.pack('<4sIIIHHHH', tag, len(data), flags, formid,
                         0, 0, FORM_VERSION, 0)
    return header + data


def group(label, data):
    header = struct.pack('<4sI4siHHHH', b'GRUP', len(data) + 24, label, 0,
                         0, 0, FORM_VERSION, 0)
    return header + data


def vmad_string(text):
    return struct.pack('<H', len(text)) + text


def vmad_script(name):
    """One script attachment with no properties."""
    return vmad_string(name) + bytes([0]) + struct.pack('<H', 0)


def vmad_object(formid, alias_index):
    """Object union in object format 2: unused, alias index, then form id."""
    return struct.pack('<HhI', 0, alias_index, formid)


def build_vmad():
    out = struct.pack('<hhH', 5, 2, 1)          # version, object format, count
    out += vmad_script(QUEST_SCRIPT)

    # Quest fragment section: no Papyrus fragments on this quest.
    out += bytes([2])                           # fragment section version
    out += struct.pack('<H', 0)                 # fragment count
    out += struct.pack('<H', 0)                 # fragment file name, empty

    # One alias (index 0), carrying one script.
    out += struct.pack('<H', 1)                 # alias count
    out += vmad_object(QUEST_FORMID, 0)
    out += struct.pack('<hhH', 5, 2, 1)         # version, object format, count
    out += vmad_script(ALIAS_SCRIPT)
    return out


def build_quest():
    data = b''
    data += subrecord(b'EDID', zstring(QUEST_EDID))
    data += subrecord(b'VMAD', build_vmad())
    # flags 0x0111 = start game enabled + run once, priority 0, no quest type.
    data += subrecord(b'DNAM', bytes([0x11, 0x01, 0x00, 0xFF,
                                      0, 0, 0, 0, 0, 0, 0, 0]))
    data += subrecord(b'NEXT', b'')             # end of the (empty) stage list
    data += subrecord(b'ANAM', struct.pack('<I', 1))     # next free alias id
    data += subrecord(b'ALST', struct.pack('<I', 0))     # alias 0
    data += subrecord(b'ALID', zstring(b'PlayerRef'))
    data += subrecord(b'FNAM', struct.pack('<I', 0))
    data += subrecord(b'ALFR', struct.pack('<I', PLAYER_REF))
    data += subrecord(b'VTCK', struct.pack('<I', 0))
    data += subrecord(b'ALED', b'')             # end of alias 0
    return record(b'QUST', 0, QUEST_FORMID, data)


def build_header(record_and_group_count, next_object_id):
    data = b''
    data += subrecord(b'HEDR', struct.pack('<fiI', HEADER_VERSION,
                                           record_and_group_count,
                                           next_object_id))
    data += subrecord(b'CNAM', zstring(AUTHOR.encode('cp1252')))
    data += subrecord(b'SNAM', zstring(DESCRIPTION.encode('cp1252')))
    for master in MASTERS:
        data += subrecord(b'MAST', zstring(master))
        data += subrecord(b'DATA', struct.pack('<Q', 0))
    data += subrecord(b'INTV', struct.pack('<I', 1))
    return record(b'TES4', ESL_FLAG, 0, data)


def build():
    quest_group = group(b'QUST', build_quest())
    # HEDR counts every record and group below the header: the group + the quest.
    header = build_header(2, (QUEST_FORMID & 0x00FFFFFF) + 1)
    return header + quest_group


if __name__ == '__main__':
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(outdir, exist_ok=True)
    dest = os.path.join(outdir, PLUGIN_NAME)
    with open(dest, 'wb') as fh:
        fh.write(build())
    print('wrote %s (%d bytes)' % (dest, os.path.getsize(dest)))
