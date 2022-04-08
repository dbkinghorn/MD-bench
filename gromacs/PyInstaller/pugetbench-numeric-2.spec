# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['../pugetbench-numeric.py'],
             pathex=['..'],
             binaries=[('../mm/micromamba', 'mm/')],
             datas=[('../run_jobs.py', '.'),
                    ('../get_sysinfo.py', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += Tree('../benchmarks', prefix = 'benchmarks') 
a.datas += Tree('../mm', prefix = 'mm', excludes = ['micromamba', 'pkgs', 'envs'])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='pugetbench-numeric',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='pugetbench-numeric')
