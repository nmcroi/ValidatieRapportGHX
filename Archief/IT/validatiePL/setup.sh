#!/bin/bash

# --- 1. Algemene logging en setup ---
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOGFILE="$PROJECT_DIR/setup.log"

exec > >(tee -a "$LOGFILE") 2>&1

echo "----- $(date) - Setup gestart -----"
echo "Projectmap: $PROJECT_DIR"

# --- 2. Python check ---
if ! command -v python3 &>/dev/null; then
    echo "FOUT: Python 3 is niet geïnstalleerd of niet in PATH."
    exit 1
fi

PYTHON="$(command -v python3)"
echo "Python-binary: $PYTHON"

# --- 3. Virtualenv ---
VENV_DIR="$PROJECT_DIR/venv"
echo "Virtual environment: $VENV_DIR"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment bestaat al: $VENV_DIR"
else
    echo "Virtual environment aanmaken..."
    $PYTHON -m venv "$VENV_DIR" || { echo "Fout bij aanmaken virtualenv"; exit 1; }
fi

# --- 4. Activatie en requirements ---
source "$VENV_DIR/bin/activate"

echo "Pip bijwerken..."
pip install --upgrade pip

REQUIREMENTS_FILE="$PROJECT_DIR/requirements/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "requirements.txt gevonden. Installatie starten..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Geen requirements.txt gevonden. Installeren standaardpackages..."
    pip install feedparser pytz openai requests beautifulsoup4 readability-lxml
fi

# --- 5. requirements.txt overschrijven voor herhaalbaarheid ---
echo "Vereisten opslaan in requirements.txt..."
pip freeze > "$REQUIREMENTS_FILE"

# --- 6. Deactivatie ---
deactivate

echo "Setup voltooid voor project: $PROJECT_DIR"
