from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_compare_and_import_sets():
    response = client.post("/api/compare", json={
        "prompt": "example", "code_a": "import os\ndef a():\n    pass\n",
        "code_b": "import sys\nclass B:\n    pass\n", "label_a": "GPT", "label_b": "Claude",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["code_a"]["label"] == "GPT"
    assert result["code_a"]["metrics"]["functions"] == 1
    assert result["code_b"]["metrics"]["classes"] == 1
    assert result["import_comparison"] == {"shared": [], "only_a": ["os"], "only_b": ["sys"]}
    assert any(item["metric"] == "functions" for item in result["differences"])


def test_one_invalid_code_does_not_break_other_analysis():
    response = client.post("/api/compare", json={"code_a": "def x()", "code_b": "x = 1"})
    assert response.status_code == 200
    result = response.json()
    assert result["code_a"]["valid_python"] is False
    assert result["code_a"]["syntax_error"]["line"] == 1
    assert result["code_b"]["valid_python"] is True
    assert result["differences"] == []


def test_empty_code_rejected():
    for key in ("code_a", "code_b"):
        payload = {"code_a": "pass", "code_b": "pass"}
        payload[key] = " \n "
        assert client.post("/api/compare", json=payload).status_code == 422


def test_ruff_reports_unused_import_without_executing_code(tmp_path):
    marker = tmp_path / "should_not_exist"
    code = f'import os\nopen({str(marker)!r}, "w").write("executed")\n'
    response = client.post("/api/compare", json={"code_a": code, "code_b": "pass"})
    assert response.status_code == 200
    result = response.json()
    assert any(issue["code"] == "F401" for issue in result["code_a"]["ruff_issues"])
    assert not marker.exists()
