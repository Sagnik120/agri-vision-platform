#!/usr/bin/env bash
# setup_venv.sh — One-time environment setup for MacBook (Apple Silicon / M5).
# Run from the repo root: bash setup/setup_venv.sh

set -e

echo "==> Checking Python version"
python3 --version

echo "==> Creating virtual environment (.venv)"
python3 -m venv .venv

echo "==> Activating venv"
source .venv/bin/activate

echo "==> Upgrading pip"
pip install --upgrade pip

echo "==> Installing requirements"
pip install -r requirements.txt

echo ""
echo "✅ Environment ready."
echo "Activate it in future terminal sessions with:"
echo "    source .venv/bin/activate"
echo ""
echo "Next steps:"
echo "  1. huggingface-cli login              # paste your HF token (account: Sagnik120)"
echo "  2. python setup/download_crop_model.py"
echo "  3. python setup/download_livestock_model.py"
echo "  4. python setup/diagnose_pipeline.py --mode auto"
