"""Double-click to open the Pinyin form using the project's environment."""

import os
from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    project = Path(__file__).resolve().parent
    python = project / ".venv" / "Scripts" / "pythonw.exe"
    if python.is_file() and Path(sys.executable).resolve() != python.resolve():
        subprocess.Popen([str(python), str(Path(__file__).resolve())], cwd=project)
    else:
        os.chdir(project)
        from mandarin_transcript.pinyin_form import main

        main()
