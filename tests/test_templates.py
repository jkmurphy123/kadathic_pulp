from pathlib import Path


EXPECTED_TEMPLATES = [
    "howard_adventure.txt",
    "lovecraft_weird.txt",
    "hybrid_weird_adventure.txt",
]


def test_style_templates_exist() -> None:
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    for name in EXPECTED_TEMPLATES:
        path = templates_dir / name
        assert path.exists(), f"Missing template: {path}"
        content = path.read_text(encoding="utf-8")
        assert "## Opening Menace" in content
        assert "## Payoff and Final Sting" in content
