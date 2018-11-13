Bio2BEL ChEBI |build| |coverage| |docs| |zenodo|
================================================
Convert the ChEBI ontology and related chemical information to BEL.

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
``bio2bel_chebi`` can be installed easily from `PyPI <https://pypi.python.org/pypi/bio2bel_chebi>`_ with
the following code in your favorite terminal:

.. code-block:: sh

    $ python3 -m pip install bio2bel_chebi

or from the latest code on `GitHub <https://github.com/bio2bel/chebi>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/bio2bel/chebi.git@master

Setup
-----
ChEBI can be downloaded and populated from either the Python REPL or the automatically
installed command line utility.

Python REPL
~~~~~~~~~~~
.. code-block:: python

    >>> import bio2bel_chebi
    >>> chebi_manager = bio2bel_chebi.Manager()
    >>> chebi_manager.populate()

Command Line Utility
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    bio2bel_chebi populate


.. |build| image:: https://travis-ci.org/bio2bel/chebi.svg?branch=master
    :target: https://travis-ci.org/bio2bel/chebi
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/bio2bel/chebi/coverage.svg?branch=master
    :target: https://codecov.io/gh/bio2bel/chebi?branch=master
    :alt: Coverage Status

.. |docs| image:: http://readthedocs.org/projects/bio2bel-chebi/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/chebi/en/latest/?badge=latest
    :alt: Documentation Status

.. |climate| image:: https://codeclimate.com/github/bio2bel/chebi/badges/gpa.svg
    :target: https://codeclimate.com/github/bio2bel/chebi
    :alt: Code Climate

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/bio2bel_chebi.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/bio2bel_chebi.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/bio2bel_chebi.svg
    :alt: MIT License

.. |zenodo| image:: https://zenodo.org/badge/97003706.svg
    :target: https://zenodo.org/badge/latestdoi/97003706
    :alt: Zenodo DOI
