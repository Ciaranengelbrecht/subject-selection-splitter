# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['extractor.py'],  # Updated path to current directory
    pathex=['/Users/CiaranIMCC/Desktop/SubjectExtract/src'],  # Add explicit path
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk',
        'PyPDF2',
        'pdf2image',
        'tqdm'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SubjectSplitter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)

app = BUNDLE(
    exe,
    name='SubjectSplitter.app',
    icon=None,
    bundle_identifier='com.ciaranengelbrecht.subjectsplitter'
)