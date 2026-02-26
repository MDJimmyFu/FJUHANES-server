import PyInstaller.__main__
import os

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(base_dir, "app.py")
templates_path = os.path.join(base_dir, "templates")
ipo_path = os.path.join(base_dir, "Ipo")

# PyInstaller command arguments
args = [
    app_path,
    '--onefile',
    '--name=AutoPrescribe',
    f'--add-data={templates_path}{os.pathsep}templates',
    f'--add-data={ipo_path}{os.pathsep}Ipo',
    '--clean',
]

# Run PyInstaller
PyInstaller.__main__.run(args)
