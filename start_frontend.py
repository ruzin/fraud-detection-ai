#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    os.chdir("frontend")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", 
            "run", "app.py", 
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()