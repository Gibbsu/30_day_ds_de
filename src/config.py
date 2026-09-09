import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DATABASE_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        DATA_DIR / "supply_chain.duckdb"
    )
)

PIPELINE_ENV = os.getenv(
    "PIPELINE_ENV",
    "development"
)
