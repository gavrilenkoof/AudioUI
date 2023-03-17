import sys
from cx_Freeze import setup, Executable
from setuptools import find_packages


include_files = ["icons"]

company_name = 'UAV'
product_name = 'AudioUI'

bdist_msi_options = {
    'upgrade_code': '{F46BA620-C027-4E68-9069-5D5D4E1FF30A}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name),
}

build_exe_options = {
    'include_files': include_files,
    'excludes': ['*'],
    "packages": [], 

}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
exe = Executable(script='main.py',
                 base=base,
                 icon='icons/mic_icon.ico',
                )

setup(  name = "AudioUI",
        version = "1.1.0",
        description = "Audio GUI",
        executables = [exe],
        options = {'bdist_msi': bdist_msi_options,
                   'build_exe': build_exe_options,
                   }

    )
