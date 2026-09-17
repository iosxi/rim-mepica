# rim-mepica

A Skyrim Special Edition mod that clears the glowing "ball" that sometimes gets
stuck beside the player's eyes. Every few seconds (10 by default, set in the
MCM) it stops the undead eye glow effects on the player.

User-facing documentation is in [docs/readme.txt](docs/readme.txt) (Japanese) —
that is the file that ships inside the archive.

## Building

```
python tools/build.py
```

Output lands in `dist/rim-mepica-<version>.zip`, laid out relative to `Data/` so
Vortex, Mod Organizer 2 and a manual install all accept it unchanged.

Requirements on the build machine:

- Skyrim Special Edition with the **Creation Kit** installed (for
  `Papyrus Compiler/PapyrusCompiler.exe` and the vanilla script sources)
- **SkyUI** installed, so `Data/SkyUI_SE.bsa` is available
- Python 3 with the `lz4` package (`pip install lz4`) — SE archives are LZ4
  compressed

Pass `--skyrim "<path>"` if the game is not at the default Steam location.

## How the pieces fit

| Path | What it is |
| --- | --- |
| `src/scripts/rimmepica_MCM.psc` | The whole mod: MCM page plus the clearing timer |
| `src/translations/*.txt` | UTF-8 translation sources, one per language |
| `src/stubs/` | Generated SkyUI declarations; compile-time only, never shipped |
| `tools/build.py` | Runs every step below and packages the result |
| `tools/bsaextract.py` | Reads SkyUI's compiled scripts out of `SkyUI_SE.bsa` |
| `tools/pex2psc.py` | Rebuilds `.psc` declarations from those `.pex` files |
| `tools/build_esp.py` | Writes `rim-mepica.esp` directly, without the Creation Kit |
| `tools/build_translations.py` | UTF-8 sources to the UTF-16 LE the game reads |
| `tools/espdump.py` | Dumps and validates a plugin; used to check the output |

`docs/format-notes.md` records where every byte of the plugin comes from, the
form IDs of the effects being stopped, and the evidence behind both.

## Design notes

**What the glow is.** Draugr, dragon priests and necromancer skeletons light
their eyes from an ability script that plays a `VisualEffect` on the *caster*
with an infinite duration and stops it only on death. When the engine hands
that script the player as the caster, the glow lands on the player and stays.
It sits where the creature's eyes would be, so it floats off the player's own
eyes. The widely quoted `player.addspell f71d1` / `removespell` trick removes
the draugr ability, but removing it does not stop the effect, so it often does
not help. The source for this diagnosis is the vanilla scripts themselves
(`DraugrFXScript.psc` and friends) and
<http://afternun.mydns.jp/blog/skyrimspecialedition/?p=1730>.

**Why poll instead of reacting.** Nothing tells a script that an effect started
playing on the player, and `VisualEffect` has no "is playing" query. `Stop()` on
an effect that is not playing does nothing, so the cheap and certain approach is
to call it on all seven effects every interval: seven native calls per tick.

**Why form IDs instead of script properties.** `Game.GetFormFromFile` keeps the
plugin free of property data, so `build_esp.py` stays identical in shape to
rim-spee's. The lookups are redone on every load, so a missing `Dawnguard.esm`
just leaves that one slot empty.

**Why an ESL-flagged plugin.** The mod is one quest record. Flagging it light
keeps it out of the 255-plugin load order budget.

## Verification status

Checked on this machine:

- the seven form IDs and editor IDs, read out of `Skyrim.esm`, `Dawnguard.esm`
  and `Dragonborn.esm`
- that the vanilla scripts play those effects with `-1` on the caster and stop
  them only on death or effect end
- the script compiles, and decompiling the result confirms it extends
  `SKI_ConfigBase` with the expected members
- `rim-mepica.esp` parses to the same structure as `rim-spee.esp`, with the VMAD
  consuming its field exactly
- every `$key` used by the script exists in every translation file (checked by
  the build)
- the translation files come out UTF-16 LE with a BOM, CRLF endings and correct
  Japanese codepoints

Checked in a running game (2026-09-17):

- a stuck eye glow on the player is removed
- the MCM page appears and works, with the Japanese translation file picked up
  (headers, option names and info text all show in Japanese)
