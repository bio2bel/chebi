# -*- coding: utf-8 -*-

"""A package for converting ChEBI to BEL.

Installation
------------
``bio2bel_chebi`` can be installed easily from `PyPI <https://pypi.python.org/pypi/bio2bel_chebi>`_ with
the following code in your favorite terminal:

.. code-block:: sh

    $ python3 -m pip install bio2bel_chebi

or from the latest code on `GitHub <https://github.com/bio2bel/chebi>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/bio2bel/chebi.git@master

Setup
-----
ChEBI can be downloaded and populated from either the Python REPL or the automatically installed command line
utility.

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

"""

from . import enrich, manager, models
from .enrich import *
from .manager import *
from .models import *

__all__ = (manager.__all__ + enrich.__all__ + models.__all__)

__version__ = '0.0.5-dev'

__title__ = 'bio2bel_chebi'
__description__ = "A package for converting ChEBI to BEL"
__url__ = 'https://github.com/bio2bel/chebi'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2017-2018 Charles Tapley Hoyt'
