from setuptools import setup

APP = ['erp-vis.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'matplotlib', 'scipy'],
    'iconfile': 'erp-vis.icns',
     'plist': 'Info.plist',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)