import PyInstaller.__main__
import os
import sys

# Define base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Data files to include (Source;Destination)
# Format: (relative_path_from_Combined_Server, destination_in_exe)
data_files = [
    # SurgerySchedule Data
    ('SurgerySchedule/templates', 'SurgerySchedule/templates'),
    ('SurgerySchedule/static', 'SurgerySchedule/static'),
    ('SurgerySchedule/eval_data', 'SurgerySchedule/eval_data'),
    ('SurgerySchedule/*.bin', 'SurgerySchedule'),
    
    # AutoPrescribe Data
    ('AutoPrescribe/templates', 'AutoPrescribe/templates'),
    ('AutoPrescribe/Ipo', 'AutoPrescribe/Ipo'),
    ('AutoPrescribe/Controlled_Drug_Sheet_P022.pdf', 'AutoPrescribe'),
]

# Convert to PyInstaller format (source;dest on Windows)
add_data_args = [f'--add-data={src};{dst}' for src, dst in data_files]

build_args = [
    'main.py',
    '--name=Combined_Server',
    '--onefile',
    '--console',
    '--paths=SurgerySchedule',
    '--paths=AutoPrescribe',
    '--hidden-import=flask',
    '--hidden-import=requests',
    '--hidden-import=jinja2',
    '--collect-all=flask',
    '--workpath=build',
    '--distpath=dist',
] + add_data_args

print(f"[*] Starting build with args: {build_args}")
PyInstaller.__main__.run(build_args)
print("[*] Build complete!")
