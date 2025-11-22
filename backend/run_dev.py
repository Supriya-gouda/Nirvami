"""Development server runner."""
import subprocess
import sys
import os

def run_dev_server():
    """Run the FastAPI development server."""
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_dev_server()
