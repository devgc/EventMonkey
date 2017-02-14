# -*- mode: python -*-

block_cipher = None


a = Analysis(
    ['EventMonkey.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('./etc/*.json', 'etc'),
        ('./etc/descriptions/*.yml', 'etc/descriptions'),
        ('./licenses/LICENSE.*','licenses'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='EventMonkey',
    debug=False,
    strip=False,
    upx=True,
    console=True
)
