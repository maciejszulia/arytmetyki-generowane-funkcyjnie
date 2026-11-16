"""README stays in step with the code: the model table has one row per model class in nna.core."""
import inspect
import re
from pathlib import Path

from nna import core

README = Path(__file__).resolve().parents[1] / "README.md"


def core_models():
    return [c for _, c in inspect.getmembers(core, inspect.isclass)
            if issubclass(c, core.Arithmetic) and c is not core.Arithmetic and c.__module__ == core.__name__]


def model_rows(text):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("| model |"))
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append(line)
    return rows


def test_readme_lists_every_core_model():
    text = README.read_text(encoding="utf-8")
    n = len(core_models())
    assert len(model_rows(text)) == n, (len(model_rows(text)), n)
    assert re.search(rf"\b{n} konkretnych modeli", text), n
