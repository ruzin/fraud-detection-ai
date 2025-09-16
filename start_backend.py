#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    os.chdir("backend")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()