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


def create_application(connection=None, url=None):
    app = Flask(__name__)
    manager = Manager(connection=connection)
    add_admin(app, manager.session, url=url)
    return app


def add_admin(app, session, **kwargs):
    admin = flask_admin.Admin(app, **kwargs)
    admin.add_view(ModelView(Chemical, session))
    admin.add_view(ModelView(Synonym, session))
    admin.add_view(ModelView(Accession, session))
    return admin


if __name__ == '__main__':
    app = create_application()
    app.run(debug=True, host='0.0.0.0', port=5000)
