#!/usr/bin/env bash
# Clara Answers — One-click demo script (macOS / Linux)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "  ============================================================"
echo "    Clara Answers — AI Voice Agent Configuration Pipeline"
echo "  ============================================================"
echo ""
echo "  This demo will:"
echo "    1. Install Python dependencies"
echo "    2. Run the full pipeline on 10 call transcripts"
echo "    3. Open the web dashboard to view results"
echo ""

# 1. Install deps
echo "  [1/3] Installing dependencies..."
echo "  -----------------------------------------------"
pip install -r requirements.txt --quiet 2>/dev/null || pip3 install -r requirements.txt --quiet
echo "  Done."

# 2. Run pipeline
echo ""
echo "  [2/3] Running the full pipeline (10 transcripts)..."
echo "  -----------------------------------------------"
cd "$SCRIPT_DIR/scripts"
python pipeline.py --mode all --clean || python3 pipeline.py --mode all --clean

# 3. Dashboard
echo ""
echo "  [3/3] Starting the web dashboard..."
echo "  -----------------------------------------------"
cd "$SCRIPT_DIR/dashboard"
echo ""
echo "  Opening http://localhost:5000 in your browser..."

# Open browser (cross-platform)
if command -v open &> /dev/null; then
    open http://localhost:5000 &
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000 &
fi

python app.py || python3 app.py
