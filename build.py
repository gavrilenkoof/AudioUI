import sys
from cx_Freeze import setup, Executable

company_name = 'UVR'
product_name = 'AudioUI'

bdist_msi_options = {
    'upgrade_code': '{F46BA620-C027-4E68-9069-5D5D4E1FF30A}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name),
    }

path = sys.path
build_exe_options = {
"path": path,
"icon": "icons/mic_icon.ico"}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
exe = Executable(script='Audio.py',
                 base=base,
                 icon='icons/mic_icon.ico',
                )

setup(  name = "AudioUI",
        version = "1.0.3",
        description = "Powerfull Calculator for all plattforms",
        executables = [exe],
        options = {'bdist_msi': bdist_msi_options})
