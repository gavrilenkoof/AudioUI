import os
import sys
from setuptools import setup

version="1.1.0"
upgrade_code = '{F46BA620-C027-4E68-9069-5D5D4E1FF30A}',

HUMAN_FRIENDLY_NAME = 'AudioUI'
HUMAN_FRIENDLY_NAME_DIR = HUMAN_FRIENDLY_NAME + f"_v{version}"

company_name = 'UAV'
product_name = HUMAN_FRIENDLY_NAME

include_files = ["icons"]



args = dict(
    name=HUMAN_FRIENDLY_NAME,
    version=version,
    description="Audio GUI",
    include_package_data=True,
)


base = "Win32GUI" if sys.platform == "win32" else None


if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
    args.setdefault('setup_requires', []).append('install_freedesktop')
    sys.argv.append('install_desktop')


if ('bdist_msi' in sys.argv) or ('build_exe' in sys.argv) or ("bdist_mac" in sys.argv):
    import cx_Freeze

    bdist_msi_options = {
        'upgrade_code': '{F46BA620-C027-4E68-9069-5D5D4E1FF30A}',
        'add_to_path': False,
        'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name),
    }
    build_exe_options = {
        'build_exe': HUMAN_FRIENDLY_NAME_DIR,
        'include_files': include_files,
        'zip_include_packages': '*',
        "zip_exclude_packages": ["scipy"],
        'excludes': [],
        "packages": [], 
    }

    bdist_mac_options = {
        "plist_items": [("NSMicrophoneUsageDescription", "Need MIC to app")],
    }

    args['options'] = {
        "bdist_msi": bdist_msi_options,
        "build_exe": build_exe_options,
        "bdist_mac": bdist_mac_options,
    }

    args["executables"] = [
        cx_Freeze.Executable(script="main.py",
                             base=base,
                             icon='icons/mic_icon.ico',
                             shortcut_name=HUMAN_FRIENDLY_NAME,
                             target_name=HUMAN_FRIENDLY_NAME,
                             ),
    ]

    cx_Freeze.setup(**args)

# setup(**args)