# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None
scripts_dir = os.path.dirname(os.path.abspath(SPEC))
root_dir = os.path.dirname(scripts_dir)

datas = [
    (os.path.join(root_dir, 'stdlib', '*.hakai'), 'stdlib'),
]

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
    ['hakai_entry.py'],
    pathex=[root_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'compiler',
        'compiler.lexer',
        'compiler.tokens',
        'compiler.parser',
        'compiler.ast_nodes',
        'compiler.semantic_analyzer',
        'compiler.intermediate_representation',
        'compiler.bytecode_generator',
        'compiler.optimizer',
        'compiler.compiler',
        'compiler.errors',
        'interpreter',
        'interpreter.interpreter',
        'interpreter.environment',
        'interpreter.runtime',
        'interpreter.values',
        'interpreter.functions',
        'interpreter.classes',
        'virtual_machine',
        'virtual_machine.instructions',
        'virtual_machine.memory',
        'virtual_machine.execution',
        'virtual_machine.vm',
        'package_manager',
        'package_manager.package',
        'package_manager.installer',
        'package_manager.resolver',
        'package_manager.repository',
        'package_manager.cli',
        'stdlib',
        'cli',
        'cli.commands',
        'cli.terminal',
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
    name='hakai',
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

