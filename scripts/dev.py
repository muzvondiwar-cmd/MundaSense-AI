"""Run the local FastAPI and Vite development servers as one supervised process."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if npm is None:
        print("npm was not found. Install Node.js 20 or newer, then run npm install in frontend/.")
        return 1

    api = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ],
        cwd=root,
    )
    time.sleep(0.6)
    if api.poll() is not None:
        print("The API failed to start. Review the error above.")
        return api.returncode or 1

    print("API: http://127.0.0.1:8000/docs")
    print("App: http://127.0.0.1:5173")
    try:
        frontend = subprocess.run(
            [npm, "run", "dev"],
            cwd=root / "frontend",
            check=False,
        )
        return frontend.returncode
    except KeyboardInterrupt:
        return 0
    finally:
        api.terminate()
        try:
            api.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api.kill()


if __name__ == "__main__":
    raise SystemExit(main())
