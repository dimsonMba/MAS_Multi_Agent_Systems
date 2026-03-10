"""
Launch the MAS simulation dashboard.

Run: python run_ui.py
Or:  streamlit run UI/app.py
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent / "UI" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path), "--server.headless", "true"])
