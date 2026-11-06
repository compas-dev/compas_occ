# Installation

## Stable

```bash
conda create -n occ -c conda-forge compas_occ
```

Several examples use the COMPAS Viewer for visualisation.
To install `compas_viewer` in the same environment

```bash
conda activate occ
conda install compas_viewer
```

## Development

To get the latest version, and install developer tools,
use a local clone of the repo.

```bash
git clone https://github.com/compas-dev/compas_occ.git
cd compas_occ
conda env create -f environment.yml
conda activate occ-dev
VIRTUAL_ENV="$CONDA_PREFIX" uv sync --active --inexact --frozen --extra dev
```

The Conda environment supplies the PythonOCC runtime. Python dependencies are
resolved by the committed uv lock. This base development environment is
sufficient for the runtime tests, wheel checks, Ruff, and source tooling.

Documentation tools and the optional viewer used by visualization examples are
installed only for the checks that need them:

```bash
VIRTUAL_ENV="$CONDA_PREFIX" uv sync --active --inexact --frozen --extra dev --extra docs --extra viz
```

`compas_viewer` is not an OCC runtime or test dependency. The `viz` extra is
needed only in the documentation environment because the authoritative
visualization examples are included in its Pyright gate. The direct commands
are canonical:

```bash
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync pytest
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync ruff check .
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync ruff format --check .
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync pyright
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync mkdocs build --strict
VIRTUAL_ENV="$CONDA_PREFIX" uv build
uvx twine check dist/*
```

The existing Invoke tasks remain as thin convenience adapters while shared
COMPAS automation still consumes them:

```bash
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync invoke test
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync invoke docs
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync invoke check
```

These tasks do not provision PythonOCC. Create or activate the Conda environment
before running them.

Formatting and lint fixes are separate, explicit local operations:

```bash
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync ruff check --fix .
VIRTUAL_ENV="$CONDA_PREFIX" uv run --active --no-sync ruff format .
```
