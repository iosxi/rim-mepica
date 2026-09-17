"""Build rim-mepica end to end.

Steps:
  1. pull SkyUI's compiled scripts out of SkyUI_SE.bsa
  2. turn them into compile-time .psc stubs (SkyUI ships no sources)
  3. compile rimmepica_MCM.psc against them
  4. generate rim-mepica.esp
  5. convert the translation files
  6. lay out a Data-relative tree and zip it for Vortex / Mod Organizer 2

Usage: python tools/build.py [--skyrim "<path to Skyrim Special Edition>"]
"""
import os
import shutil
import re
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
BUILD = os.path.join(ROOT, 'build')
DIST = os.path.join(ROOT, 'dist')

PLUGIN_BASE = 'rim-mepica'
SCRIPT_NAME = 'rimmepica_MCM'
VERSION = '1.0.0'

DEFAULT_SKYRIM = (r'C:\Program Files (x86)\Steam\steamapps\common'
                  r'\Skyrim Special Edition')

SKYUI_SCRIPTS = ['ski_questbase', 'ski_configbase', 'ski_playerloadgamealias',
                 'ski_configmanager']


def run(args):
    print('>', ' '.join(str(a) for a in args))
    result = subprocess.run(args, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    if result.returncode != 0:
        raise SystemExit('step failed: %s' % args[0])
    return result.stdout


def python(script, *args):
    return run([sys.executable, os.path.join(TOOLS, script)] + list(args))


def check_translation_keys():
    """Every $key the script uses must exist in every translation file."""
    source = open(os.path.join(ROOT, 'src', 'scripts', SCRIPT_NAME + '.psc'),
                  encoding='utf-8').read()
    used = set(re.findall(r'"(\$rimmepica_[A-Za-z0-9_]+)"', source))
    problems = []
    tdir = os.path.join(ROOT, 'src', 'translations')
    for name in sorted(os.listdir(tdir)):
        if not name.endswith('.txt'):
            continue
        defined = set()
        for line in open(os.path.join(tdir, name), encoding='utf-8'):
            if line.startswith('$') and '\t' in line:
                defined.add(line.split('\t', 1)[0])
        missing = used - defined
        unused = defined - used
        if missing:
            problems.append('%s is missing %s' % (name, sorted(missing)))
        if unused:
            print('note: %s defines unused keys %s' % (name, sorted(unused)))
    if problems:
        raise SystemExit('translation check failed:\n  ' +
                         '\n  '.join(problems))
    print('translation check: %d keys present in every language' % len(used))


def main():
    skyrim = DEFAULT_SKYRIM
    if '--skyrim' in sys.argv:
        skyrim = sys.argv[sys.argv.index('--skyrim') + 1]
    compiler = os.path.join(skyrim, 'Papyrus Compiler', 'PapyrusCompiler.exe')
    if not os.path.isfile(compiler):
        raise SystemExit('Papyrus compiler not found at ' + compiler)

    if os.path.isdir(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(BUILD)

    # 1 + 2: SkyUI stubs.
    bsa = os.path.join(skyrim, 'Data', 'SkyUI_SE.bsa')
    if not os.path.isfile(bsa):
        raise SystemExit('SkyUI_SE.bsa not found at ' + bsa)
    for name in SKYUI_SCRIPTS:
        python('bsaextract.py', bsa, name, os.path.join(BUILD, 'skyui'))
    stubs = os.path.join(ROOT, 'src', 'stubs')
    python('pex2psc.py', stubs,
           *[os.path.join(BUILD, 'skyui', 'scripts', n + '.pex')
             for n in SKYUI_SCRIPTS])

    # 3: compile.
    check_translation_keys()
    scripts_out = os.path.join(BUILD, 'Scripts')
    os.makedirs(scripts_out, exist_ok=True)
    imports = ';'.join([
        os.path.join(ROOT, 'src', 'scripts'),
        stubs,
        os.path.join(skyrim, 'Data', 'Scripts', 'Source'),
        os.path.join(skyrim, 'Data', 'source', 'scripts'),
    ])
    out = run([compiler, SCRIPT_NAME, '-f=TESV_Papyrus_Flags.flg',
               '-i=' + imports, '-o=' + scripts_out])
    if 'Compilation succeeded' not in out:
        raise SystemExit('Papyrus compilation did not report success')

    # 4 + 5: plugin and translations.
    python('build_esp.py', BUILD)
    python('build_translations.py', os.path.join(ROOT, 'src', 'translations'),
           os.path.join(BUILD, 'Interface', 'Translations'), PLUGIN_BASE)

    # 6: lay out the Data-relative tree.
    stage = os.path.join(BUILD, 'stage')
    layout = {
        PLUGIN_BASE + '.esp': os.path.join(BUILD, PLUGIN_BASE + '.esp'),
        'Scripts/%s.pex' % SCRIPT_NAME:
            os.path.join(scripts_out, SCRIPT_NAME + '.pex'),
        'Source/Scripts/%s.psc' % SCRIPT_NAME:
            os.path.join(ROOT, 'src', 'scripts', SCRIPT_NAME + '.psc'),
        'Interface/Translations/%s_english.txt' % PLUGIN_BASE:
            os.path.join(BUILD, 'Interface', 'Translations',
                         PLUGIN_BASE + '_english.txt'),
        'Interface/Translations/%s_japanese.txt' % PLUGIN_BASE:
            os.path.join(BUILD, 'Interface', 'Translations',
                         PLUGIN_BASE + '_japanese.txt'),
        'readme.txt': os.path.join(ROOT, 'docs', 'readme.txt'),
    }
    for rel, src in layout.items():
        if not os.path.isfile(src):
            raise SystemExit('missing build output: ' + src)
        dest = os.path.join(stage, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(src, dest)

    os.makedirs(DIST, exist_ok=True)
    archive = os.path.join(DIST, '%s-%s.zip' % (PLUGIN_BASE, VERSION))
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel in sorted(layout):
            zf.write(os.path.join(stage, rel.replace('/', os.sep)), rel)
    print('\npackaged %s' % archive)
    for rel in sorted(layout):
        print('  ' + rel)


if __name__ == '__main__':
    main()
