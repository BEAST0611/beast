"""Sync pages/ re-exports from views/ modules."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWS = ROOT / "views"
PAGES = ROOT / "pages"
PAGES.mkdir(exist_ok=True)

MODULES = [
    "dashboard", "data_import", "round_tripping", "bank_verification", "idle_cash",
    "signatory_validation", "ai_copilot", "marketplace", "training_hub", "reporting", "administration",
]

for mod in MODULES:
    content = f"from views.{mod} import render\n"
    (PAGES / f"{mod}.py").write_text(content, encoding="utf-8")
    print(f"Synced pages/{mod}.py")
