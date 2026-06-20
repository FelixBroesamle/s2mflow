s2mflow: Multicommodity Flow Instance Generator
===============================================

.. s2mflow documentation master file.

Welcome to the official documentation for **s2mflow**.
This library provides a high-performance tool for generating 
multicommodity flow instances from single-commodity flow instances.

Introduction
------------
`s2mflow` bridges the gap between theoretical multicommodity flow research and practical
optimization by providing a robust generator implemented in Rust with a seamless Python
interface via PyO3.

Installation
------------

`s2mflow` can be installed across different environment depending on whether you are using the pre-compiled package or building from source.

**Standard Python Installation**

You can install `s2mflow` directly via `pip` (or `poetry`):

.. code-block:: bash
   
   pip install s2mflow
   # Or using Poetry
   poetry add s2mflow

**Building from Source**

If you want to build `s2mflow` from source, ensure you have the Rust toolchain installed, then run:

.. code-block:: bash

   git clone https://github.com/FelixBroesamle/s2mflow.git
   cd s2mflow
   poetry install -vvv
   poetry run maturin develop --release

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   workflows
   format

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide:

   api

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`