********************************************************************************
Installation
********************************************************************************

Stable
======

:mod:`compas_occ` can be installed using `pip`.
However, some of its dependencies have to be installed from `conda`.
Therefore, the recommended installation procedure is to create a `conda` environment
with the required dependencies, and then install :mod:`compas_occ` in that environment with `pip`

.. code-block:: bash

    conda create -n occ python=3.8 compas compas_view2 pythonocc-core
    conda activate occ
    pip install compas_occ


Development
===========

To get the latest development version, you can install from local source, or directly from the github repo.

.. code-block:: bash

    conda create -n occ python=3.8 compas compas_view2 pythonocc-core
    conda activate occ
    pip install git+https://github.com/compas-dev/compas_occ.git#egg=compas_occ

.. code-block:: bash

    conda create -n occ python=3.8 compas compas_view2 pythonocc-core
    conda activate occ
    git pull https://github.com/compas-dev/compas_occ.git#egg=compas_occ
    cd compas_occ
    pip install -e .
