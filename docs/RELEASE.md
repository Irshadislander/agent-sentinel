# Release Checklist

This repo uses tags like `v0.1.1`.

## 0) Bump version

Update `pyproject.toml`:

```toml
[project]
version = "X.Y.Z"
```

## 1) Clean state + tests

```bash
git switch main
git pull --ff-only
python -m pip install -e ".[dev]"
pre-commit run --all-files
pytest -q
agent-sentinel-benchmark --policy configs/policies/default.yaml
agent-sentinel-ui --help
```

## 2) Build artifacts locally

```bash
python -m pip install -U build
python -m build
ls -la dist/
```

## 3) Validate install from wheel (fresh venv)

```bash
python -m venv /tmp/as_test_venv
source /tmp/as_test_venv/bin/activate
python -m pip install -U pip
python -m pip install dist/*.whl
python -c "import agent_sentinel; print('OK', agent_sentinel.__file__)"
agent-sentinel-benchmark --policy configs/policies/default.yaml
agent-sentinel-ui --help
deactivate
```

## 4) Tag and push

```bash
git tag -a vX.Y.Z -m "vX.Y.Z: <message>"
git push origin vX.Y.Z
```

## 5) GitHub release (optional)

```bash
gh release create vX.Y.Z --generate-notes
```

## Notes

- If `gh pr create` says "no commits between ...", you have not committed anything on that branch yet.
- Do not paste comment lines starting with `#` directly into `zsh` if copied weirdly; run commands line-by-line.
