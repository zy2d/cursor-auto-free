# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['cursor_pro_keep_alive.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.ini', '.'),
        ('turnstilePatch', 'turnstilePatch'),
        ('cursor_auth_manager.py', '.'),
    ],
    hiddenimports=[
        'cursor_auth_manager'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CursorPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)

app = BUNDLE(
    exe,
    name='CursorPro.app',
    icon=None,
    bundle_identifier='com.yourcompany.cursorpro',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
    },
) 