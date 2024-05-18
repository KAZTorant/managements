import os
import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install pip and PyInstaller."""
    subprocess.check_call([sys.executable, '-m', 'pip',
                          'install', '--upgrade', 'pip'])
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'pyinstaller'])


def collect_static():
    """Collect static files."""
    subprocess.check_call([sys.executable, 'manage.py',
                          'collectstatic', '--noinput'])


def generate_spec_file():
    """Generate the initial .spec file using PyInstaller."""
    subprocess.check_call(
        ['pyinstaller', '--name=BirC', '--onefile', 'manage.py'])


def modify_spec_file():
    """Modify the generated .spec file to include static and template directories."""
    spec_file_path = "BirC.spec"

    with open(spec_file_path, "r") as f:
        spec_content = f.readlines()

    # Find the Analysis section
    for i, line in enumerate(spec_content):
        if line.strip().startswith("a = Analysis("):
            analysis_index = i
            break
    else:
        raise ValueError(
            "Could not find the Analysis section in the .spec file.")

    BASE_DIR = Path(__file__).resolve().parent

    # Paths to static and template directories
    datas = [
        # Path to collected static files
        (f"{str(BASE_DIR / 'staticfiles')}", "static"),
        (f"{str(BASE_DIR / 'templates')}", "templates")
    ]

    datas_str = ",\n        ".join(
        f"('{src}', '{dest}')" for src, dest in datas)

    new_datas_line = f"    datas=[{datas_str}],\n"

    # Check if datas already exist and modify accordingly
    for i, line in enumerate(spec_content[analysis_index:], start=analysis_index):
        if line.strip().startswith("datas="):
            spec_content[i] = new_datas_line
            break
    else:
        spec_content.insert(analysis_index + 1, new_datas_line)

    with open(spec_file_path, "w") as f:
        f.writelines(spec_content)


def build_executable():
    """Run PyInstaller to build the executable."""
    subprocess.check_call([sys.executable, '-m', 'PyInstaller', 'BirC.spec'])


def main():
    try:
        install_dependencies()
        collect_static()
        generate_spec_file()
        modify_spec_file()
        build_executable()
        print("Executable created successfully. Check the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the build process: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
