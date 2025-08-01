#!/usr/bin/env python3
"""
Simple script to update poetry.lock with new dependencies
"""
import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("Updating poetry.lock with new dependencies...")
    
    # Try to install poetry if not available
    success, stdout, stderr = run_command("poetry --version")
    if not success:
        print("Poetry not found. Installing poetry...")
        success, stdout, stderr = run_command("pip install poetry")
        if not success:
            print("Failed to install poetry. Please install it manually.")
            return False
    
    # Add the new dependency
    print("Adding prometheus-client dependency...")
    success, stdout, stderr = run_command("poetry add prometheus-client")
    if not success:
        print(f"Failed to add dependency: {stderr}")
        return False
    
    print("Dependency added successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 