# rim-mepica

> **English version below.** This document is in Japanese first, followed by
> the same content in English — see [English](#english).

## 日本語

Skyrim Special Edition 用の MOD です。プレイヤーの目のそばに、光る「玉」の
ようなものが残って消えなくなることがあります。この MOD はその光を一定間隔
（既定 10 秒、MCM で変更可）で消します。消す対象は、アンデッドの「目の光」の
エフェクトです。

遊ぶ人向けの説明書は [docs/readme.txt](docs/readme.txt)（日本語）です。
配布する zip に入るのはこのファイルです。

### ビルド

```
python tools/build.py
```

`dist/rim-mepica-<バージョン>.zip` が出力されます。中身は `Data/` からの相対
パスで並んでいるので、Vortex・Mod Organizer 2・手動導入のどれでもそのまま
入ります。

ビルドする PC に必要なもの：

- **Creation Kit** を入れた Skyrim Special Edition
  （`Papyrus Compiler/PapyrusCompiler.exe` とバニラのスクリプトソースを使うため）
- **SkyUI**（`Data/SkyUI_SE.bsa` を使うため）
- Python 3 と `lz4` パッケージ（`pip install lz4`）。SE の BSA は LZ4 で
  圧縮されているため

ゲームが Steam の既定の場所にない場合は `--skyrim "<パス>"` を付けてください。

### ファイル構成

| パス | 内容 |
| --- | --- |
| `src/scripts/rimmepica_MCM.psc` | MOD の本体。MCM ページと、光を消すタイマー |
| `src/translations/*.txt` | 翻訳の元ファイル（UTF-8、1 言語 1 ファイル） |
| `src/stubs/` | 自動生成した SkyUI の宣言。コンパイル時だけ使い、配布しない |
| `tools/build.py` | 以下の手順をすべて実行し、zip にまとめる |
| `tools/bsaextract.py` | `SkyUI_SE.bsa` から SkyUI のコンパイル済みスクリプトを取り出す |
| `tools/pex2psc.py` | その `.pex` から `.psc` の宣言を復元する |
| `tools/build_esp.py` | Creation Kit を使わずに `rim-mepica.esp` を直接書き出す |
| `tools/build_translations.py` | UTF-8 の元ファイルを、ゲームが読む UTF-16 LE に変換する |
| `tools/espdump.py` | プラグインの中身を表示・検証する。出力の確認に使う |

[docs/format-notes.md](docs/format-notes.md) には、プラグインの各バイトの由来、
消しているエフェクトの FormID、それぞれの根拠をまとめています。

### 設計メモ

**光の正体。** ドラウグル・ドラゴンプリースト・死霊術師のスケルトンは、能力の
スクリプトで自分の目を光らせています。このスクリプトは `VisualEffect` を
*caster*（使い手）に対して無期限で再生し、止めるのは死んだときだけです。
ゲーム側がこのスクリプトに caster としてプレイヤーを渡してしまうと、光が
プレイヤーに付いたまま残ります。光はその敵の目があるはずの位置に付くので、
プレイヤー自身の目からはズレて浮いて見えます。よく紹介されている
`player.addspell f71d1` / `removespell` はドラウグルの能力を付け外しするだけで、
能力を外してもエフェクトは止まらないため、効かないことが多いです。この判断の
根拠は、バニラのスクリプトそのもの（`DraugrFXScript.psc` など）と
<http://afternun.mydns.jp/blog/skyrimspecialedition/?p=1730> です。

**イベントで反応せず、定期的に処理する理由。** エフェクトがプレイヤーに再生され
始めたことをスクリプトに知らせる仕組みはなく、`VisualEffect` には「再生中か」を
調べる関数もありません。再生されていないエフェクトに `Stop()` を呼んでも何も
起きないので、7 つのエフェクトすべてに一定間隔で `Stop()` を呼ぶのが、軽くて
確実なやり方です。1 回の処理はネイティブ関数 7 回の呼び出しです。

**スクリプトのプロパティではなく FormID で探す理由。** `Game.GetFormFromFile` を
使うと、プラグインにプロパティのデータを持たせずに済みます。そのため
`build_esp.py` は rim-spee と同じ形のままにできます。検索はロードのたびに
やり直すので、`Dawnguard.esm` がない環境でもその 1 つが空になるだけです。

**ESL フラグ付きプラグインにする理由。** この MOD のレコードはクエスト 1 つ
だけです。軽量プラグインにしておけば、255 個のプラグイン枠を使いません。

### 検証状況

この PC 上で確認したこと：

- 7 つの FormID とエディター ID（`Skyrim.esm`・`Dawnguard.esm`・`Dragonborn.esm`
  から読み出したもの）
- バニラのスクリプトが、それらのエフェクトを caster に `-1`（無期限）で再生し、
  止めるのは死亡時かエフェクト終了時だけであること
- スクリプトがコンパイルでき、生成物を逆コンパイルすると `SKI_ConfigBase` を継承し、
  想定どおりのメンバーを持っていること
- `rim-mepica.esp` を解析すると `rim-spee.esp` と同じ構造で、VMAD がちょうど
  過不足なく読み切れること
- スクリプトが使う `$キー` が、すべての翻訳ファイルにあること（ビルド時に確認）
- 翻訳ファイルが BOM 付き UTF-16 LE・CRLF 改行で出力され、日本語の文字が
  正しいこと

実際にゲームを起動して確認したこと（2026-09-17）：

- プレイヤーに残った目の光が消えること
- MCM ページが表示されて操作でき、日本語の翻訳ファイルが読み込まれること
  （見出し・項目名・説明文がすべて日本語で表示される）

---

## English

A Skyrim Special Edition mod that clears the glowing "ball" that sometimes gets
stuck beside the player's eyes. Every few seconds (10 by default, set in the
MCM) it stops the undead eye glow effects on the player.

User-facing documentation is in [docs/readme.txt](docs/readme.txt) (Japanese) —
that is the file that ships inside the archive.

### Building

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

### How the pieces fit

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

[docs/format-notes.md](docs/format-notes.md) records where every byte of the
plugin comes from, the form IDs of the effects being stopped, and the evidence
behind both.

### Design notes

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

### Verification status

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
