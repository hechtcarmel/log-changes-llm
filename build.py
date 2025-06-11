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
    # Run PyInstaller with the spec file
    PyInstaller.__main__.run([
        'CampaignChangesAnalyzer.spec',
        '--clean',
        '--noconfirm'
    ])

    print("\n\nBuild process finished.")
    
    # Provide instructions
    dist_path = os.path.join('dist', 'CampaignChangesAnalyzer')
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