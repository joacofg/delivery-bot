from __future__ import annotations

from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "Sistema de Análisis Inteligente para Operaciones Rappi - Dummy Data (1) (1).xlsx"

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
