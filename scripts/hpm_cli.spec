# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None
scripts_dir = os.path.dirname(os.path.abspath(SPEC))
root_dir = os.path.dirname(scripts_dir)

excludes = [
    'PySide6',
    'shiboken6',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'cv2',
    'tkinter',
    'pytest',
]

a = Analysis(
    ['hpm_entry.py'],
    pathex=[root_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'package_manager',
        'package_manager.package',
        'package_manager.installer',
        'package_manager.resolver',
        'package_manager.repository',
        'package_manager.cli',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='hpm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

