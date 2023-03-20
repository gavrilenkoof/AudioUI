import os
import sys
from setuptools import setup


HUMAN_FRIENDLY_NAME = 'AudioUI'

company_name = 'UAV'
product_name = HUMAN_FRIENDLY_NAME

version="1.1.0"
upgrade_code = '{F46BA620-C027-4E68-9069-5D5D4E1FF30A}',

include_files = ["icons"]

args = dict(
    name=HUMAN_FRIENDLY_NAME,
    version=version,
    description="Audio GUI",
)



if ('bdist_msi' in sys.argv) or ('build_exe' in sys.argv):
    import cx_Freeze

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

    args['options'] = {
        "bdist_msi": bdist_msi_options,
        "build_exe": build_exe_options,
    }

    args["executables"] = [
        cx_Freeze.Executable(script="main.py",
                             base="Win32GUI",
                             icon='icons/mic_icon.ico',
                             shortcutName=HUMAN_FRIENDLY_NAME),
    ]

    cx_Freeze.setup(args)