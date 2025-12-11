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
```