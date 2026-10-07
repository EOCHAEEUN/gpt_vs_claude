import json
import subprocess
import tempfile
from pathlib import Path

from app.schemas.compare import RuffIssue


def analyze_ruff(code: str) -> tuple[list[RuffIssue], str | None]:
    with tempfile.TemporaryDirectory(prefix="code-contrast-") as directory:
        path = Path(directory) / "input.py"
        path.write_text(code, encoding="utf-8")
        try:
            result = subprocess.run(
                ["ruff", "check", str(path), "--output-format=json", "--isolated"],
                capture_output=True, text=True, timeout=10, check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as error:
            return [], f"Ruff unavailable: {error}"
        if result.returncode not in (0, 1):
            return [], result.stderr.strip() or "Ruff failed"
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return [], "Ruff returned invalid JSON"
        issues = [RuffIssue(
            code=item["code"], message=item["message"],
            line=item["location"]["row"], column=item["location"]["column"],
        ) for item in data]
        return issues, None
