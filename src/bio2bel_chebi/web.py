# -*- coding: utf-8 -*-

""" This module contains the flask application to visualize the db

when pip installing

.. source-code:: sh

    pip install bio2bel_chebi[web]

"""

import flask_admin
from flask import Flask
from flask_admin.contrib.sqla import ModelView

from bio2bel_chebi.manager import Manager
from bio2bel_chebi.models import *

app = Flask(__name__)
admin = flask_admin.Admin(app, url='/')

manager = Manager()

admin.add_view(ModelView(Chemical, manager.session))
admin.add_view(ModelView(Synonym, manager.session))
admin.add_view(ModelView(Accession, manager.session))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
