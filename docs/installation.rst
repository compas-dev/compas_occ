********************************************************************************
Installation
********************************************************************************

Stable
======

Stable releases of :mod:`compas_occ` can be installed via ``conda-forge``.

.. code-block:: bash

    conda create -n occ -c conda-forge compas_occ

Several examples use the COMPAS Viewer for visualisation.
To install :mod:`compas_viewer` in the same environment

.. code-block:: bash

    conda activate occ
    pip install compas_viewer


Development
===========

To get the latest development version, you can install from local source, or directly from the github repo.

.. code-block:: bash

    conda create -n occ -c conda-forge compas pythonocc-core
    conda activate occ
    git clone https://github.com/compas-dev/compas_occ.git
    cd compas_occ
    pip install -e ".[dev]"
