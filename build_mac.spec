# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for macOS application
Creates: AI_Rescheduling_Agent.app
"""

import os
from pathlib import Path

block_cipher = None

# Get the directory where this spec file is located
spec_dir = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include templates
        ('templates', 'templates'),
        # Include static files
        ('static', 'static'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'pandas',
        'openpyxl',
        'requests',
        'dotenv',
        'jinja2',
        'werkzeug',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.random._examples',
        'IPython',
        'jupyter',
        'notebook',
    ],
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
    name='AI_Rescheduling_Agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console on macOS (use .app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='AI_Rescheduling_Agent.app',
    icon=None,  # Add 'icon.icns' here if you have one
    bundle_identifier='com.yourcompany.ai-rescheduling-agent',
    info_plist={
        'CFBundleName': 'AI Rescheduling Agent',
        'CFBundleDisplayName': 'AI Rescheduling Agent',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': False,
    },
)