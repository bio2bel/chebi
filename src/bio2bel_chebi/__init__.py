# -*- coding: utf-8 -*-

from . import enrich, manager, models
from .enrich import *
from .manager import *
from .models import *

__all__ = (manager.__all__ + enrich.__all__ + models.__all__)

__version__ = '0.0.4'

__title__ = 'bio2bel_chebi'
__description__ = "A package for converting ChEBI to BEL"
__url__ = 'https://github.com/bio2bel/chebi'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2017-2018 Charles Tapley Hoyt'
