# -*- coding: utf-8 -*-

import os
import re
import sys

sys.path.insert(0, os.path.abspath('../../src'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'Bio2BEL ChEBI'
copyright = '2017-2018, Charles Tapley Hoyt'
author = 'Charles Tapley Hoyt'

release = '0.2.2-dev'

parsed_version = re.match(
    '(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-(?P<release>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?',
    release
)
version = parsed_version.expand('\g<major>.\g<minor>.\g<patch>')

if parsed_version.group('release'):
    tags.add('prerelease')

language = None
exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = True
html_theme = 'sphinx_rtd_theme'
html_static_path = []
htmlhelp_basename = 'bioebel_chebidoc'
latex_elements = {}
latex_documents = [
    (master_doc, 'bio2bel_chebi.tex', 'Bio2BEL ChEBI Documentation', 'Charles Tapley Hoyt', 'manual'),
]
man_pages = [
    (master_doc, 'Bio2BEL ChEBI', 'Bio2BEL ChEBI Documentation', [author], 1)
]
texinfo_documents = [
    (master_doc, 'Bio2BEL ChEBI', 'Bio2BEL ChEBI Documentation', author, 'Bio2BEL ChEBI', 'Serialize ChEBI to BEL', 'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'networkx': ('https://networkx.github.io/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/latest', None),
    'pybel': ('https://pybel.readthedocs.io/en/latest/', None),
}

autodoc_member_order = 'bysource'
autoclass_content = 'both'

if os.environ.get('READTHEDOCS'):
    tags.add('readthedocs')
