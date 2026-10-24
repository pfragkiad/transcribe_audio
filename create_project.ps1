# Create Python 3.14 virtual environment
py -3.14 -m venv .venv

# Activate environment
.\.venv\Scripts\Activate.ps1

# Upgrade installation tools
python -m pip install --upgrade pip setuptools wheel

# Test if whisper CAN be installed
# python -m pip install --dry-run --only-binary=:all: faster-whisper

# Install transcription dependencies
python -m pip install faster-whisper

# to reinstall
# python -m pip install -r requirements.txt