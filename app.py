from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]   # يرجع لروت المشروع
df = pd.read_csv(ROOT / "data" / "sample_programs.csv")
