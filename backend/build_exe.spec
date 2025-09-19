# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 현재 디렉토리
backend_dir = Path('C:/Users/rulru/Git/MDFVisualization/backend')
project_dir = backend_dir.parent

block_cipher = None

a = Analysis(
    ['main_standalone.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=[
        # 정적 파일들 (HTML, JS, CSS)
        (str(project_dir / 'index.html'), '.'),
        (str(project_dir / 'mdf-viewer-backend.js'), '.'),
        (str(project_dir / 'singlechart-popup.html'), '.'),
        (str(project_dir / 'doublechart-popup.html'), '.'),
        # 기타 필요한 파일들
        ('models.py', '.'),
        ('mdf_processor.py', '.'),
    ],
    hiddenimports=[
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan.on',
        'asammdf',
        'fastapi',
        'pydantic',
        'numpy',
        'pandas',
        'lxml',
        'numexpr',
        'python_dateutil',
        'multipart',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='MDF_Viewer_Server_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 콘솔 창 표시
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)