import os
import platform
import subprocess
import sys

try:
    import PyInstaller.__main__
except ImportError:
    print("PyInstaller is not installed. Please install it by running:")
    print("pip install pyinstaller")
    sys.exit(1)

def build():
    """
    Builds the application using PyInstaller.
    """
    app_name = "CampaignChangesAnalyzer"
    entry_script = "app.py"

    # Common PyInstaller options
    pyinstaller_options = [
        '--name', app_name,
        '--onefile',
        '--clean',
        '--noconfirm',
        # Collect data for Gradio and its dependencies
        '--collect-data=gradio',
        '--collect-data=gradio_client',
        # Pandas often requires its data to be collected
        '--collect-data=pandas',
        # The gradio-calendar component might need its data.
        '--collect-data=gradio_calendar',
    ]
    
    # OS-specific options
    if platform.system() == "Windows":
        # Creates a .exe and hides the console window
        pyinstaller_options.append('--windowed')
    elif platform.system() == "Darwin": # macOS
        # Creates a .app bundle
        pyinstaller_options.append('--windowed')


    # Add the entry script to the command
    full_command = pyinstaller_options + [entry_script]
    
    print(f"Running PyInstaller with command: {' '.join(['pyinstaller'] + full_command)}")

    # Run PyInstaller
    PyInstaller.__main__.run(full_command)

    print("\n\nBuild process finished.")
    
    # Provide instructions
    dist_path = os.path.join('dist', app_name)
    if platform.system() == "Darwin":
        dist_path += ".app"
        print(f"Executable bundle created at: {dist_path}")
        print("To run the application, you can double-click it in Finder or use:")
        print(f"open '{dist_path}'")
    elif platform.system() == "Windows":
        dist_path += ".exe"
        print(f"Executable created at: {dist_path}")
        print("You can now run the application from the 'dist' folder.")
    else: # Linux
        print(f"Executable created at: {dist_path}")
        print("You can now run the application from the 'dist' folder.")


if __name__ == "__main__":
    build() 