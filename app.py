"""
SpidyCAD // Team AlgoRhythm
Master Streamlit Cloud Entrypoint (app.py)
"""
from pathlib import Path
import sys

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Execute the complete SpidyCAD HUD application
FRONTEND_APP = ROOT_DIR / "frontend" / "app.py"
with open(FRONTEND_APP, "rb") as f:
    code = compile(f.read(), str(FRONTEND_APP), "exec")
    exec(code, globals())
