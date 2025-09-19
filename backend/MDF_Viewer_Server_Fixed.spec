# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_standalone.py'],
    pathex=[],
    binaries=[],
    datas=[('models.py', '.'), ('mdf_processor.py', '.'), ('../index.html', '.'), ('../mdf-viewer-backend.js', '.'), ('../singlechart-popup.html', '.'), ('../doublechart-popup.html', '.')],
    hiddenimports=['uvicorn.loops.auto', 'uvicorn.protocols.http.auto'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'tensorflow', 'matplotlib'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MDF_Viewer_Server_Fixed',
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
)
