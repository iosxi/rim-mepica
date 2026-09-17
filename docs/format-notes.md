# Where the plugin layout came from

`tools/build_esp.py` writes `rim-mepica.esp` by hand rather than through the
Creation Kit, so every field in it needs a reason. These are the notes behind
those values; they were read out of files on this machine, not from memory.

## Reference plugins

The layout was derived by decoding MCM plugins that the game already loads,
using `tools/espdump.py`:

| Plugin | Why it was useful |
| --- | --- |
| `PhotoMode.esp` | The minimal case: one quest, one script, no script properties. The VMAD parse consumes all 73 bytes exactly, which pins the whole structure down. |
| `SmoothCam.esp`, `BetterThirdPersonSelection.esp` | Confirm the same shape with a `ModName` string property and a second master. |
| `SkyClimb.esp` | Confirms the alias section with two alias scripts. |

`rim-mepica.esp` parses to the same structure as `PhotoMode.esp`, differing only
in names and lengths.

## QUST VMAD

The subrecord is, in order:

```
int16   version            = 5
int16   objectFormat       = 2
uint16  scriptCount        = 1
  wstring scriptName       = "rimmepica_MCM"
  uint8   status           = 0
  uint16  propertyCount    = 0
uint8   fragmentSectionVersion = 2
uint16  fragmentCount      = 0
wstring fragmentFileName   = ""
uint16  aliasCount         = 1
  uint16 unused            = 0        \
  int16  aliasIndex        = 0         | object union, objectFormat 2
  uint32 formId            = quest id  /
  int16  version           = 5
  int16  objectFormat      = 2
  uint16 scriptCount       = 1
    wstring scriptName     = "SKI_PlayerLoadGameAlias"
    uint8   status         = 0
    uint16  propertyCount  = 0
```

The object union's field order (`unused`, `aliasIndex`, `formId` — not the other
way round) was settled by the last property in `Hotkey Quit.esp`: its bytes are
`00 00 FF FF 14 00 00 00`, which only reads sensibly as alias `-1` and form
`0x14`, i.e. `PlayerRef`.

## Other fields

- **TES4 flag `0x200`** marks the file as a light plugin, so it takes no slot in
  the 255-plugin load order. All four reference plugins set it.
- **Record form version 44** is what Skyrim SE stamps on records.
- **Form ID `0x01000800`.** The high byte is an index into the plugin's master
  list, and a value equal to the number of masters means "this file". With one
  master that is `0x01`. Light plugins must keep their object index inside
  `0x800`–`0xFFF`.
- **`DNAM` = `11 01 00 FF 00…`** is flags `0x0111` (start game enabled, run
  once), priority 0. Copied from `PhotoMode.esp`, which matches `SmoothCam.esp`.
- **`ALFR` = `0x00000014`** is `PlayerRef` in `Skyrim.esm`, which sits at index 0
  of our master list, so the ID needs no remapping.

## Why an alias at all

The quest needs to know when a save has been loaded, so it can restart its
polling loop. Decoding `ski_playerloadgamealias.pex` shows the script does
exactly one thing: on `OnPlayerLoadGame` it calls `GetOwningQuest()`, casts to
`SKI_QuestBase`, and calls `OnGameReload()` on it.

That matters because it only ever notifies **its own** quest — SkyUI does not
broadcast the event to other mods. So `OnGameReload()` will not fire for
`rimmepica_MCM` unless this plugin attaches that alias script itself. Every MCM
plugin examined here does the same thing.

## SkyUI stubs

SkyUI ships compiled scripts only, but the Papyrus compiler needs source for
every ancestor. `tools/pex2psc.py` reconstructs declarations straight out of
`SkyUI_SE.bsa`, so the signatures come from the exact SkyUI build installed
rather than from a copied-out header. The stubs have empty bodies and are never
distributed; at runtime SkyUI's real scripts are what load.

Skyrim `.pex` files are **big-endian**, unlike the plugin format. Inside a
function record, `numInstructions` is a `uint16`, and `VariableData` type tags
are `0` null, `1` identifier, `2` string, `3` int32, `4` float, `5` bool.

## The eye glow effects

The script stops these `VisualEffect` (`RFCT`) records on the player. The list
was produced by walking every `RFCT` record in the three masters and keeping the
ones whose editor ID mentions an eye; `Dragonborn.esm` has none.

| File | Form ID | Editor ID | Played by |
| --- | --- | --- | --- |
| `Skyrim.esm` | `000A8527` | `FXDraugrFemaleEyeEffect` | `DraugrFXScript`, `FxDraugrMagicScript` |
| `Skyrim.esm` | `000ABEE8` | `FXDraugrMaleEyeEffect` | `DraugrFXScript`, `FxDraugrMagicScript` |
| `Skyrim.esm` | `000AA856` | `FXDragonPreistEyeGlowEffect` | `DragonPriestActorScript` |
| `Skyrim.esm` | `000EB87A` | `FXSkeletonNecroEyeGlowEffect` | `FXSkeletonNecroScript` |
| `Skyrim.esm` | `000EBE9E` | `FXSkeletonNecroPriestEyeGlowEffect` | (necro priest variant) |
| `Skyrim.esm` | `000F9065` | `FXMG07DogEyeGlowEffect` | `FXMG07DogScript` |
| `Dawnguard.esm` | `02006AF4` | `DLC1SoulCairnFXSkeletonNecroEyeGlowEffect` | `DLC1SoulCairnCreatureFX` |

`Game.GetFormFromFile` takes the ID without the load order byte, so the
Dawnguard entry is passed as `0x00006AF4`.

Every one of those scripts is an `ActiveMagicEffect` that does
`selfRef = caster` and then `EyeGlowFX.Play(selfRef, -1)`: a negative duration
means forever, and the matching `Stop` only runs in `OnDying` / `OnDeath` /
`OnEffectFinish`. If the engine ever passes the player as `caster`, the glow is
attached to the player and nothing ever removes it. The effect is placed at the
creature's eye nodes, which is why it floats off the player's actual eyes.

Calling `Stop` on an effect that is not playing is harmless: the vanilla
`DLC1SoulCairnCreatureFX` does exactly that for sleeping creatures, calling
`FXSCCreatureMultiEffect.Stop(selfRef)` without ever having played it.
