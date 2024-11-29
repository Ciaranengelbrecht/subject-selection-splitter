# macos.spec
block_cipher = None

# Get Poppler path from environment
import os
poppler_path = os.getenv('POPPLER_PATH', '/opt/homebrew/bin')
poppler_lib = os.getenv('POPPLER_LIB', '/opt/homebrew/lib')

a = Analysis(
    ['src/extractor.py'],
    pathex=[],
    binaries=[
        (os.path.join(poppler_path, 'pdftoppm'), '.'),
        (os.path.join(poppler_path, 'pdfinfo'), '.'),
        (os.path.join(poppler_lib, 'libpoppler.dylib'), '.'),
        (os.path.join(poppler_lib, 'libpoppler-cpp.dylib'), '.')
    ],
    datas=[],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk',
        'PyPDF2',
        'pdf2image',
        'tqdm',
        'pathlib',
        'zipfile',
        'io',
        'os',
        'json',
        'datetime'
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
    name='SubjectSelectionSplitter-Mac',
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
    name='SubjectSelectionSplitter-Mac.app',
    icon=None,
    bundle_identifier='com.ciaranengelbrecht.subjectsplitter',
    info_plist={
        'CFBundleName': 'Subject Selection Splitter',
        'CFBundleDisplayName': 'Subject Selection Splitter',
        'CFBundleExecutable': 'SubjectSelectionSplitter-Mac',
        'CFBundleIdentifier': 'com.ciaranengelbrecht.subjectsplitter',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '10.10',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False
    }
)