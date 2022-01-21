********************************************************************************
Installation
********************************************************************************

Stable
======

Install with conda
------------------

In an existing environment, for example "research".

.. code-block:: bash

    conda install -n research compas_occ compas_view2 --yes


In a new environment, for example ... "research" 😀

.. code-block:: bash

    conda create -n research compas_occ compas_view2 --yes


In both cases, :mod:`compas_view2` is optional.


Install with pip
----------------

To install :mod:`compas_occ` with ``pip``, some of its dependencies have to be installed from ``conda-forge`` first.

.. code-block:: bash

    conda create -n research compas compas_view2 pythonocc-core
    conda activate occ
    pip install compas_occ


Development
===========

To get the latest development version, you can install from local source, or directly from the github repo.

.. code-block:: bash

    conda create -n occ python=3.9 compas compas_view2 pythonocc-core
    conda activate occ
    pip install git+https://github.com/compas-dev/compas_occ.git#egg=compas_occ

.. code-block:: bash

    conda create -n occ python=3.9 compas compas_view2 pythonocc-core
    conda activate occ
    git pull https://github.com/compas-dev/compas_occ.git#egg=compas_occ
    cd compas_occ
    pip install -e .


You can use whichever Python version you prefer, but ``3.9`` is compatible with Blender...