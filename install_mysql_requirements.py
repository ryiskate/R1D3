#!/usr/bin/env python
"""
Script to install MySQL requirements for the R1D3 project.
This script:
1. Installs the required packages for MySQL
2. Verifies the installation
"""
import subprocess
import sys
import importlib.util

def check_package_installed(package_name):
    """Check if a package is installed."""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except ModuleNotFoundError:
        return False

def install_package(package_name):
    """Install a package using pip."""
    print(f"Installing {package_name}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"Successfully installed {package_name}")
        return True
    else:
        print(f"Failed to install {package_name}")
        print(f"Error: {result.stderr}")
        return False

def main():
    """Main function to install required packages."""
    required_packages = [
        "dj-database-url",
        "mysqlclient",
        "python-dotenv"
    ]
    
    print("Checking and installing required packages for MySQL...")
    
    for package in required_packages:
        if check_package_installed(package.replace("-", "_")):
            print(f"{package} is already installed")
        else:
            install_package(package)
    
    # Verify installations
    all_installed = True
    for package in required_packages:
        package_name = package.replace("-", "_")
        if not check_package_installed(package_name):
            print(f"WARNING: {package} is still not installed")
            all_installed = False
    
    if all_installed:
        print("\nAll required packages are installed!")
        print("\nYou can now run:")
        print("  python configure_pythonanywhere_mysql.py --username YOUR_USERNAME --password YOUR_MYSQL_PASSWORD")
        print("\nThen follow the instructions to complete the MySQL setup.")
    else:
        print("\nSome packages failed to install. Please try installing them manually:")
        print("  pip install dj-database-url mysqlclient python-dotenv")

if __name__ == "__main__":
    main()
