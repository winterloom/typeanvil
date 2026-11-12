import importlib.util
import pathlib

import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "homebrew_formula.py"
_spec = importlib.util.spec_from_file_location("homebrew_formula", _p)
hf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hf)

V = "2026.10.0"


def _sums(skip=None):
    lines = []
    for i, t in enumerate(hf.TARGETS.values()):
        if t == skip:
            continue
        lines.append(f"{str(i + 1) * 64}  typeanvil-{V}-{t}.tar.gz")
    lines.append(f"{'f' * 64}  typeanvil-{V}-x86_64-unknown-linux-gnu.tar.gz")
    return "\n".join(lines) + "\n"


def test_formula_selects_per_platform_artifact_and_sha():
    out = hf.render(V, hf.parse_sums(_sums()), "o/r")
    for i, t in enumerate(hf.TARGETS.values()):
        assert f"releases/download/v{V}/typeanvil-{V}-{t}.tar.gz" in out
        assert f'sha256 "{str(i + 1) * 64}"' in out
    assert 'version "2026.10.0"' in out
    assert "on_arm do" in out and "on_intel do" in out
    assert "--version" in out and "render" in out


def test_missing_target_fails():
    with pytest.raises(ValueError, match="aarch64-apple-darwin"):
        hf.render(V, hf.parse_sums(_sums(skip="aarch64-apple-darwin")), "o/r")


def test_non_calver_rejected():
    with pytest.raises(ValueError):
        hf.render("1.0", hf.parse_sums(_sums()), "o/r")


def test_cli_writes_file(tmp_path):
    s = tmp_path / "SHA256SUMS"
    s.write_text(_sums())
    o = tmp_path / "typeanvil.rb"
    assert hf.main(["--version", V, "--sums", str(s), "-o", str(o)]) == 0
    assert o.read_text().startswith("# Generated")
