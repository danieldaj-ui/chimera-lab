#!/usr/bin/env python3
"""Package the compiled plugin library as a VST3 bundle.

macOS: ad-hoc signed bundle from target/release/libchimera_plugin.dylib.
Windows: VST3 bundle folder from chimera_plugin.dll, using the standard layout
    Chimera Lab.vst3/Contents/x86_64-win/Chimera Lab.vst3

Usage: bundle.py [output_dir] [--lib path/to/library]
"""
import argparse, pathlib, plistlib, shutil, subprocess, sys

root = pathlib.Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument('out', nargs='?', default=str(root / 'target/bundled'))
ap.add_argument('--lib', help='compiled library to package (default: auto-detect)')
ap.add_argument('--platform', choices=['mac', 'windows'],
                help='bundle layout (default: the current OS)')
args = ap.parse_args()

out = pathlib.Path(args.out).resolve()
platform = args.platform or ('windows' if sys.platform == 'win32' else 'mac')
bundle = out / 'Chimera Lab.vst3'
contents = bundle / 'Contents'


def find_lib(names):
    if args.lib:
        return pathlib.Path(args.lib).resolve()
    candidates = [root / 'target' / 'release' / n for n in names]
    candidates += sorted((root / 'target').glob('*/release/' + names[0]))
    for c in candidates:
        if c.is_file():
            return c
    raise SystemExit('Compiled plugin not found. Run: cargo build --locked --release -p chimera-plugin')


if platform == 'windows':
    lib = find_lib(['chimera_plugin.dll'])
    if bundle.exists():
        shutil.rmtree(bundle)
    (contents / 'x86_64-win').mkdir(parents=True)
    shutil.copy2(lib, contents / 'x86_64-win' / 'Chimera Lab.vst3')
    (contents / 'Resources').mkdir()
else:
    lib = find_lib(['libchimera_plugin.dylib'])
    (contents / 'MacOS').mkdir(parents=True, exist_ok=True)
    shutil.copy2(lib, contents / 'MacOS/Chimera Lab')
    with (contents / 'Info.plist').open('wb') as f:
        plistlib.dump(dict(CFBundleExecutable='Chimera Lab', CFBundleIdentifier='org.chimera-community.lab',
            CFBundleName='Chimera Lab', CFBundleDisplayName='Chimera Lab', CFBundlePackageType='BNDL',
            CFBundleSignature='????', CFBundleShortVersionString='0.4.0', CFBundleVersion='0.4.0',
            NSHighResolutionCapable=True), f)
    (contents / 'PkgInfo').write_text('BNDL????')
    subprocess.run(['codesign', '--force', '--sign', '-', str(bundle)], check=True)
    subprocess.run(['codesign', '--verify', '--strict', str(bundle)], check=True)
print(bundle)
