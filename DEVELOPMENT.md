# Development guide

## Environment

Create the project-local environment and install the development dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

The repository intentionally uses the standard-library `venv` module and `pip`. Run tools
through `.venv/bin/python` to avoid depending on shell activation or a global Python
environment.

On Windows, replace `.venv/bin/python` with `.\.venv\Scripts\python.exe`.

## Project layout

```text
.
├── data/                         # Example input images and derived data
├── notebooks/                    # Interactive analysis workflow
├── src/hippocampus_reidi/
│   ├── analysis.py               # Color metrics and batch processing
│   └── color_picker.py           # OpenCV and notebook color pickers
├── tests/                        # Tests using synthetic images
└── pyproject.toml                # Package, dependency, and tool configuration
```

## Quality checks

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

The public API is exported from `src/hippocampus_reidi/__init__.py`. Keep notebook imports
on the installed `hippocampus_reidi` package; do not modify `sys.path` or import the `src`
directory as a package.
